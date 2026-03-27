"""
Amazon S3 service wrapper with mock and real implementations.
Handles incident photo and evidence file storage.
Author: Adithya Reddy Madireddy
"""

import uuid
import base64
from datetime import datetime, timezone


class S3Service:
    """
    Service class for interacting with Amazon S3.
    When USE_AWS is False, upload operations return mock URLs
    and files are tracked in memory for local development.
    """

    def __init__(self, app=None):
        """Initialize the S3 service with optional Flask app configuration."""
        self.use_aws = False
        self.region = 'eu-west-1'
        self.bucket_name = 'safety-incident-photos'
        self.client = None
        self._mock_files = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Configure the service from the Flask app settings."""
        self.use_aws = app.config.get('USE_AWS', False)
        self.region = app.config.get('AWS_REGION', 'eu-west-1')
        self.bucket_name = app.config.get('S3_BUCKET_NAME', 'safety-incident-photos')
        if self.use_aws:
            import boto3
            self.client = boto3.client('s3', region_name=self.region)

    def upload_file(self, file_data, filename, content_type='image/jpeg'):
        """
        Upload a file to S3 and return the public URL.
        In mock mode, stores metadata and returns a simulated URL.

        Args:
            file_data: The binary file content.
            filename: The desired filename in the bucket.
            content_type: MIME type of the file.
        Returns:
            Dictionary with upload status and URL.
        """
        file_key = f'incidents/{uuid.uuid4().hex}/{filename}'

        if self.use_aws and self.client:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data,
                ContentType=content_type
            )
            url = f'https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}'
            return {'status': 'success', 'url': url, 'key': file_key}

        # Mock mode: store file metadata in memory
        mock_url = f'https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}'
        self._mock_files[file_key] = {
            'filename': filename,
            'content_type': content_type,
            'size': len(file_data) if file_data else 0,
            'uploaded_at': datetime.now(timezone.utc).isoformat(),
            'url': mock_url
        }
        return {
            'status': 'success',
            'message': 'Mock: file uploaded successfully',
            'url': mock_url,
            'key': file_key
        }

    def delete_file(self, file_key):
        """
        Delete a file from S3 by its key.
        Returns a status dictionary indicating success.
        """
        if self.use_aws and self.client:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return {'status': 'success', 'key': file_key}

        # Mock mode: remove from memory
        self._mock_files.pop(file_key, None)
        return {'status': 'success', 'message': f'Mock: file {file_key} deleted'}

    def list_files(self, prefix='incidents/'):
        """
        List all files in the bucket under the given prefix.
        Returns a list of file metadata dictionaries.
        """
        if self.use_aws and self.client:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            return [
                {'key': obj['Key'], 'size': obj['Size'],
                 'last_modified': obj['LastModified'].isoformat()}
                for obj in response.get('Contents', [])
            ]

        # Mock mode: filter by prefix
        return [
            {'key': k, 'size': v['size'], 'last_modified': v['uploaded_at']}
            for k, v in self._mock_files.items()
            if k.startswith(prefix)
        ]

    def get_presigned_url(self, file_key, expiration=3600):
        """
        Generate a presigned URL for temporary access to a private file.
        Returns the URL string.
        """
        if self.use_aws and self.client:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url

        # Mock mode: return a simulated presigned URL
        return f'https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}?mock-signed=true&expires={expiration}'

    def get_status(self):
        """Return the current status of the S3 service for health checks."""
        if self.use_aws:
            try:
                self.client.head_bucket(Bucket=self.bucket_name)
                return {
                    'service': 'Amazon S3',
                    'status': 'connected',
                    'mode': 'production',
                    'bucket': self.bucket_name,
                    'region': self.region
                }
            except Exception as e:
                return {
                    'service': 'Amazon S3',
                    'status': 'error',
                    'mode': 'production',
                    'error': str(e)
                }
        return {
            'service': 'Amazon S3',
            'status': 'mock',
            'mode': 'development',
            'bucket': self.bucket_name,
            'files_stored': len(self._mock_files)
        }
