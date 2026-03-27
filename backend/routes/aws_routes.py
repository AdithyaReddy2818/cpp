"""
AWS service status and interaction routes.
Provides endpoints to check the health and status of all AWS services
and to trigger AWS-dependent operations like geocoding and notifications.
Author: Adithya Reddy Madireddy
"""

from flask import Blueprint, request, jsonify

aws_bp = Blueprint('aws', __name__)

# Service instances are set during app initialization
dynamodb_service = None
s3_service = None
sns_service = None
location_service = None
ses_service = None
lambda_service = None


def init_aws_routes(dynamo, s3, sns, location, ses, lam):
    """
    Inject AWS service instances into the routes module.
    Called during Flask app initialization.
    """
    global dynamodb_service, s3_service, sns_service
    global location_service, ses_service, lambda_service
    dynamodb_service = dynamo
    s3_service = s3
    sns_service = sns
    location_service = location
    ses_service = ses
    lambda_service = lam


@aws_bp.route('/api/aws/status', methods=['GET'])
def get_all_aws_status():
    """Return the health status of all six AWS services."""
    try:
        statuses = {
            'dynamodb': dynamodb_service.get_status() if dynamodb_service else {'status': 'not configured'},
            's3': s3_service.get_status() if s3_service else {'status': 'not configured'},
            'sns': sns_service.get_status() if sns_service else {'status': 'not configured'},
            'location': location_service.get_status() if location_service else {'status': 'not configured'},
            'ses': ses_service.get_status() if ses_service else {'status': 'not configured'},
            'lambda': lambda_service.get_status() if lambda_service else {'status': 'not configured'}
        }
        return jsonify(statuses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/geocode', methods=['POST'])
def geocode_address():
    """Geocode an address using Amazon Location Service."""
    try:
        data = request.get_json()
        if not data or 'address' not in data:
            return jsonify({'error': 'address is required'}), 400

        result = location_service.geocode_address(data['address'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/reverse-geocode', methods=['POST'])
def reverse_geocode():
    """Reverse geocode coordinates to an address using Amazon Location Service."""
    try:
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'latitude and longitude are required'}), 400

        result = location_service.reverse_geocode(data['latitude'], data['longitude'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/notify', methods=['POST'])
def send_notification():
    """Send a push notification via Amazon SNS."""
    try:
        data = request.get_json()
        if not data or 'subject' not in data or 'message' not in data:
            return jsonify({'error': 'subject and message are required'}), 400

        result = sns_service.publish_notification(data['subject'], data['message'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/email', methods=['POST'])
def send_email():
    """Send an email via Amazon SES."""
    try:
        data = request.get_json()
        required = ['to', 'subject', 'body']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        result = ses_service.send_email(data['to'], data['subject'], data['body'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/classify', methods=['POST'])
def classify_incident():
    """Classify an incident severity using AWS Lambda."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Incident data is required'}), 400

        result = lambda_service.classify_incident(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/upload', methods=['POST'])
def upload_file():
    """Upload a file to Amazon S3."""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({'error': 'filename is required'}), 400

        file_data = data.get('data', b'')
        if isinstance(file_data, str):
            file_data = file_data.encode()

        result = s3_service.upload_file(
            file_data,
            data['filename'],
            data.get('content_type', 'image/jpeg')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
