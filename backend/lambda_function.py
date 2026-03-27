import json
import boto3
import os
import uuid
import time
import hashlib
import hmac
import base64
import secrets
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

# Environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'safetyreports-prod')
S3_BUCKET = os.environ.get('S3_BUCKET', 'safetyreports-images-prod-adithya')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
REGION = os.environ.get('REGION', 'eu-west-1')
JWT_SECRET = os.environ.get('JWT_SECRET', 'safetyreports-secret-2026')

# AWS clients
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)
s3 = boto3.client('s3', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# CORS headers applied to every response
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
}

INCIDENT_CATEGORIES = [
    'theft', 'vandalism', 'assault', 'suspicious_activity',
    'noise_complaint', 'traffic', 'fire', 'environmental', 'other'
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, default=str)
    }


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 else int(obj)
    raise TypeError


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o) if o % 1 else int(o)
        return super().default(o)


def to_dynamo(data):
    """Convert floats/ints to Decimal for DynamoDB."""
    if isinstance(data, dict):
        return {k: to_dynamo(v) for k, v in data.items()}
    if isinstance(data, list):
        return [to_dynamo(i) for i in data]
    if isinstance(data, float):
        return Decimal(str(data))
    if isinstance(data, int) and not isinstance(data, bool):
        return Decimal(str(data))
    return data


def from_dynamo(data):
    """Convert Decimals back to native Python types."""
    if isinstance(data, dict):
        return {k: from_dynamo(v) for k, v in data.items()}
    if isinstance(data, list):
        return [from_dynamo(i) for i in data]
    if isinstance(data, Decimal):
        return float(data) if data % 1 else int(data)
    return data


# ---------------------------------------------------------------------------
# JWT helpers (base64.header.payload.hmac)
# ---------------------------------------------------------------------------

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += '=' * padding
    return base64.urlsafe_b64decode(s)


def create_token(payload: dict) -> str:
    header = b64url_encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
    payload['iat'] = int(time.time())
    payload['exp'] = int(time.time()) + 86400  # 24 hours
    payload_encoded = b64url_encode(json.dumps(payload).encode())
    signature_input = f'{header}.{payload_encoded}'.encode()
    signature = hmac.new(JWT_SECRET.encode(), signature_input, hashlib.sha256).digest()
    sig_encoded = b64url_encode(signature)
    return f'{header}.{payload_encoded}.{sig_encoded}'


def verify_token(token: str) -> dict:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header, payload_encoded, sig_encoded = parts
        signature_input = f'{header}.{payload_encoded}'.encode()
        expected_sig = hmac.new(JWT_SECRET.encode(), signature_input, hashlib.sha256).digest()
        actual_sig = b64url_decode(sig_encoded)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload = json.loads(b64url_decode(payload_encoded))
        if payload.get('exp', 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def get_user_from_token(headers):
    auth = headers.get('Authorization') or headers.get('authorization', '')
    if auth.startswith('Bearer '):
        token = auth[7:]
    else:
        token = auth
    if not token:
        return None
    return verify_token(token)


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> dict:
    salt = secrets.token_hex(32)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return {'salt': salt, 'hash': pw_hash.hex()}


def verify_password(password: str, salt: str, pw_hash: str) -> bool:
    computed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hmac.compare_digest(computed.hex(), pw_hash)


# ---------------------------------------------------------------------------
# Auto-classify incident category
# ---------------------------------------------------------------------------

def auto_classify(title, description):
    text = f'{title} {description}'.lower()
    keywords = {
        'theft': ['stolen', 'theft', 'rob', 'burgl', 'shopli'],
        'vandalism': ['vandal', 'graffiti', 'broken window', 'damage', 'smash'],
        'assault': ['assault', 'attack', 'fight', 'hit', 'punch', 'violen'],
        'suspicious_activity': ['suspicious', 'lurk', 'stalk', 'unknown person', 'stranger'],
        'noise_complaint': ['noise', 'loud', 'music', 'party', 'bark'],
        'traffic': ['traffic', 'speeding', 'accident', 'crash', 'parking'],
        'fire': ['fire', 'smoke', 'burn', 'flame', 'arson'],
        'environmental': ['pollution', 'dump', 'waste', 'litter', 'spill', 'flood'],
    }
    for category, words in keywords.items():
        for w in words:
            if w in text:
                return category
    return 'other'


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

# AUTH ---

def handle_register(body):
    if not body:
        return response(400, {'error': 'Request body required'})
    username = body.get('username', '').strip()
    email = body.get('email', '').strip()
    password = body.get('password', '')
    if not username or not email or not password:
        return response(400, {'error': 'username, email, and password are required'})

    # Check existing user
    result = table.scan(FilterExpression=Attr('entityType').eq('user') & Attr('email').eq(email))
    if result.get('Items'):
        return response(409, {'error': 'Email already registered'})

    pw_data = hash_password(password)
    user_id = str(uuid.uuid4())
    item = to_dynamo({
        'id': user_id,
        'entityType': 'user',
        'username': username,
        'email': email,
        'passwordHash': pw_data['hash'],
        'salt': pw_data['salt'],
        'createdAt': int(time.time())
    })
    table.put_item(Item=item)
    token = create_token({'userId': user_id, 'username': username, 'email': email})
    return response(201, {
        'message': 'User registered successfully',
        'token': token,
        'user': {'id': user_id, 'username': username, 'email': email}
    })


def handle_login(body):
    if not body:
        return response(400, {'error': 'Request body required'})
    email = body.get('email', '').strip()
    password = body.get('password', '')
    if not email or not password:
        return response(400, {'error': 'email and password are required'})

    result = table.scan(FilterExpression=Attr('entityType').eq('user') & Attr('email').eq(email))
    users = result.get('Items', [])
    if not users:
        return response(401, {'error': 'Invalid email or password'})

    user = users[0]
    if not verify_password(password, user['salt'], user['passwordHash']):
        return response(401, {'error': 'Invalid email or password'})

    token = create_token({
        'userId': user['id'],
        'username': user['username'],
        'email': user['email']
    })
    return response(200, {
        'message': 'Login successful',
        'token': token,
        'user': from_dynamo({
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        })
    })


# INCIDENTS ---

def handle_get_incidents(params):
    result = table.scan(FilterExpression=Attr('entityType').eq('incident'))
    items = result.get('Items', [])

    # Query param filtering
    if params:
        category = params.get('category')
        status = params.get('status')
        if category:
            items = [i for i in items if i.get('category') == category]
        if status:
            items = [i for i in items if i.get('status') == status]

    items = sorted(items, key=lambda x: x.get('createdAt', 0), reverse=True)
    return response(200, {'incidents': from_dynamo(items)})


def handle_create_incident(body, user):
    if not body:
        return response(400, {'error': 'Request body required'})
    title = body.get('title', '').strip()
    description = body.get('description', '').strip()
    if not title or not description:
        return response(400, {'error': 'title and description are required'})

    category = body.get('category', '').strip()
    if not category:
        category = auto_classify(title, description)

    incident_id = str(uuid.uuid4())
    now = int(time.time())
    item = {
        'id': incident_id,
        'entityType': 'incident',
        'title': title,
        'description': description,
        'category': category,
        'location': body.get('location', ''),
        'latitude': body.get('latitude'),
        'longitude': body.get('longitude'),
        'status': 'open',
        'reportedBy': user.get('userId', ''),
        'reportedByUsername': user.get('username', ''),
        'createdAt': now,
        'updatedAt': now
    }
    # Remove None values
    item = {k: v for k, v in item.items() if v is not None}
    table.put_item(Item=to_dynamo(item))

    # Publish SNS notification
    try:
        if SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f'New Safety Incident: {title}',
                Message=(
                    f'A new incident has been reported.\n\n'
                    f'Title: {title}\n'
                    f'Category: {category}\n'
                    f'Location: {item.get("location", "N/A")}\n'
                    f'Description: {description}\n'
                    f'Reported by: {user.get("username", "Unknown")}\n'
                    f'Time: {now}'
                )
            )
    except Exception as e:
        print(f'SNS publish error: {e}')

    return response(201, {'message': 'Incident created', 'incident': from_dynamo(item)})


def handle_get_incident(incident_id):
    result = table.get_item(Key={'id': incident_id})
    item = result.get('Item')
    if not item or item.get('entityType') != 'incident':
        return response(404, {'error': 'Incident not found'})
    return response(200, {'incident': from_dynamo(item)})


def handle_update_incident(incident_id, body):
    if not body:
        return response(400, {'error': 'Request body required'})

    result = table.get_item(Key={'id': incident_id})
    item = result.get('Item')
    if not item or item.get('entityType') != 'incident':
        return response(404, {'error': 'Incident not found'})

    allowed_fields = ['title', 'description', 'category', 'location',
                      'latitude', 'longitude', 'status', 'adminNotes']
    update_expr_parts = []
    expr_values = {}
    expr_names = {}
    for field in allowed_fields:
        if field in body:
            safe_name = f'#{field}'
            safe_val = f':{field}'
            update_expr_parts.append(f'{safe_name} = {safe_val}')
            expr_names[safe_name] = field
            expr_values[safe_val] = body[field]

    if not update_expr_parts:
        return response(400, {'error': 'No valid fields to update'})

    update_expr_parts.append('#updatedAt = :updatedAt')
    expr_names['#updatedAt'] = 'updatedAt'
    expr_values[':updatedAt'] = int(time.time())

    table.update_item(
        Key={'id': incident_id},
        UpdateExpression='SET ' + ', '.join(update_expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=to_dynamo(expr_values)
    )

    updated = table.get_item(Key={'id': incident_id}).get('Item', {})
    return response(200, {'message': 'Incident updated', 'incident': from_dynamo(updated)})


def handle_delete_incident(incident_id):
    result = table.get_item(Key={'id': incident_id})
    item = result.get('Item')
    if not item or item.get('entityType') != 'incident':
        return response(404, {'error': 'Incident not found'})

    table.delete_item(Key={'id': incident_id})
    return response(200, {'message': 'Incident deleted'})


# IMAGE ---

def handle_upload_image(incident_id, body):
    if not body or not body.get('image'):
        return response(400, {'error': 'image (base64) is required'})

    result = table.get_item(Key={'id': incident_id})
    item = result.get('Item')
    if not item or item.get('entityType') != 'incident':
        return response(404, {'error': 'Incident not found'})

    try:
        image_data = base64.b64decode(body['image'])
    except Exception:
        return response(400, {'error': 'Invalid base64 image data'})

    image_key = f'incidents/{incident_id}/{uuid.uuid4()}.jpg'
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=image_key,
        Body=image_data,
        ContentType='image/jpeg'
    )
    image_url = f'https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{image_key}'

    # Append to images list
    existing_images = item.get('images', [])
    if isinstance(existing_images, str):
        existing_images = [existing_images]
    existing_images.append(image_url)

    table.update_item(
        Key={'id': incident_id},
        UpdateExpression='SET images = :imgs, updatedAt = :ts',
        ExpressionAttributeValues=to_dynamo({
            ':imgs': existing_images,
            ':ts': int(time.time())
        })
    )
    return response(200, {'message': 'Image uploaded', 'imageUrl': image_url})


# DASHBOARD ---

def handle_dashboard():
    result = table.scan(FilterExpression=Attr('entityType').eq('incident'))
    items = result.get('Items', [])

    total = len(items)
    open_count = sum(1 for i in items if i.get('status') == 'open')
    resolved_count = sum(1 for i in items if i.get('status') == 'resolved')

    by_category = {}
    for i in items:
        cat = i.get('category', 'other')
        by_category[cat] = by_category.get(cat, 0) + 1

    sorted_items = sorted(items, key=lambda x: x.get('createdAt', 0), reverse=True)
    recent = sorted_items[:10]

    return response(200, {
        'totalIncidents': total,
        'openCount': open_count,
        'resolvedCount': resolved_count,
        'byCategoryCount': by_category,
        'recentIncidents': from_dynamo(recent)
    })


# ADMIN STATUS ---

def handle_update_status(incident_id, body):
    if not body or 'status' not in body:
        return response(400, {'error': 'status is required'})

    valid_statuses = ['open', 'investigating', 'resolved', 'closed']
    new_status = body['status']
    if new_status not in valid_statuses:
        return response(400, {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'})

    result = table.get_item(Key={'id': incident_id})
    item = result.get('Item')
    if not item or item.get('entityType') != 'incident':
        return response(404, {'error': 'Incident not found'})

    table.update_item(
        Key={'id': incident_id},
        UpdateExpression='SET #s = :s, updatedAt = :ts',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues=to_dynamo({
            ':s': new_status,
            ':ts': int(time.time())
        })
    )

    return response(200, {'message': f'Status updated to {new_status}'})


# NOTIFICATIONS (PUBLIC) ---

def handle_subscribe(body):
    if not body or not body.get('email'):
        return response(400, {'error': 'email is required'})

    if not SNS_TOPIC_ARN:
        return response(500, {'error': 'SNS topic not configured'})

    try:
        sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=body['email']
        )
        return response(200, {'message': 'Subscription requested. Check your email to confirm.'})
    except Exception as e:
        print(f'SNS subscribe error: {e}')
        return response(500, {'error': 'Failed to subscribe'})


def handle_subscribers():
    if not SNS_TOPIC_ARN:
        return response(200, {'count': 0})
    try:
        result = sns.list_subscriptions_by_topic(TopicArn=SNS_TOPIC_ARN)
        subs = [s for s in result.get('Subscriptions', []) if s.get('SubscriptionArn') != 'PendingConfirmation']
        return response(200, {'count': len(subs)})
    except Exception as e:
        print(f'SNS list error: {e}')
        return response(200, {'count': 0})


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

def lambda_handler(event, context):
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    headers = event.get('headers') or {}
    params = event.get('queryStringParameters') or {}
    path_params = event.get('pathParameters') or {}

    # Parse body
    body = None
    raw_body = event.get('body')
    if raw_body:
        try:
            body = json.loads(raw_body)
        except (json.JSONDecodeError, TypeError):
            body = None

    # OPTIONS preflight — always first
    if http_method == 'OPTIONS':
        return response(200, {'message': 'OK'})

    # PUBLIC notification routes — before auth check
    if path == '/subscribe' and http_method == 'POST':
        return handle_subscribe(body)
    if path == '/subscribers' and http_method == 'GET':
        return handle_subscribers()

    # AUTH routes (no token required)
    if path == '/auth/register' and http_method == 'POST':
        return handle_register(body)
    if path == '/auth/login' and http_method == 'POST':
        return handle_login(body)

    # All other routes require authentication
    user = get_user_from_token(headers)
    if not user:
        return response(401, {'error': 'Unauthorized. Valid token required.'})

    # INCIDENT routes
    if path == '/incidents' and http_method == 'GET':
        return handle_get_incidents(params)

    if path == '/incidents' and http_method == 'POST':
        return handle_create_incident(body, user)

    # Routes with incident ID
    # Match /incidents/{id}/image
    if path.startswith('/incidents/') and path.endswith('/image') and http_method == 'POST':
        incident_id = path.split('/')[2]
        return handle_upload_image(incident_id, body)

    # Match /incidents/{id}/status
    if path.startswith('/incidents/') and path.endswith('/status') and http_method == 'PUT':
        incident_id = path.split('/')[2]
        return handle_update_status(incident_id, body)

    # Match /incidents/{id}
    if path.startswith('/incidents/') and path.count('/') == 2:
        incident_id = path.split('/')[2]
        if http_method == 'GET':
            return handle_get_incident(incident_id)
        if http_method == 'PUT':
            return handle_update_incident(incident_id, body)
        if http_method == 'DELETE':
            return handle_delete_incident(incident_id)

    # DASHBOARD
    if path == '/dashboard' and http_method == 'GET':
        return handle_dashboard()

    return response(404, {'error': 'Route not found'})
