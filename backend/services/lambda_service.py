"""
AWS Lambda service wrapper with mock and real implementations.
Handles asynchronous incident processing and severity classification.
Author: Adithya Reddy Madireddy
"""

import json
import uuid
from datetime import datetime, timezone


class LambdaService:
    """
    Service class for interacting with AWS Lambda.
    Invokes Lambda functions for asynchronous incident processing,
    such as severity classification, photo analysis, and report generation.
    In mock mode, processing logic runs locally.
    """

    def __init__(self, app=None):
        """Initialize the Lambda service with optional Flask app configuration."""
        self.use_aws = False
        self.region = 'eu-west-1'
        self.function_name = 'safety-incident-processor'
        self.client = None
        self._mock_invocations = []
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Configure the service from the Flask app settings."""
        self.use_aws = app.config.get('USE_AWS', False)
        self.region = app.config.get('AWS_REGION', 'eu-west-1')
        self.function_name = app.config.get('LAMBDA_FUNCTION_NAME', 'safety-incident-processor')
        if self.use_aws:
            import boto3
            self.client = boto3.client('lambda', region_name=self.region)

    def invoke_function(self, function_name, payload):
        """
        Invoke a Lambda function with the given payload.

        Args:
            function_name: The Lambda function name or ARN.
            payload: Dictionary to pass as the event payload.
        Returns:
            Dictionary with invocation status and response payload.
        """
        if self.use_aws and self.client:
            response = self.client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            response_payload = json.loads(response['Payload'].read())
            return {
                'status': 'success',
                'status_code': response['StatusCode'],
                'payload': response_payload
            }

        # Mock mode: simulate the invocation locally
        result = self._mock_process(function_name, payload)
        invocation = {
            'id': str(uuid.uuid4()),
            'function': function_name,
            'payload': payload,
            'result': result,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self._mock_invocations.append(invocation)
        return {
            'status': 'success',
            'message': 'Mock: function invoked locally',
            'payload': result
        }

    def classify_incident(self, incident_data):
        """
        Invoke the severity classification Lambda function for an incident.
        Analyses incident category, description keywords, and time of day
        to assign a severity and priority score.
        """
        payload = {
            'action': 'classify',
            'incident': incident_data
        }
        return self.invoke_function(self.function_name, payload)

    def process_incident_async(self, incident_id, action='full_process'):
        """
        Trigger asynchronous processing of an incident.
        This includes severity re-evaluation, notification dispatch, and analytics update.
        """
        payload = {
            'action': action,
            'incident_id': incident_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        if self.use_aws and self.client:
            response = self.client.invoke(
                FunctionName=self.function_name,
                InvocationType='Event',  # Asynchronous invocation
                Payload=json.dumps(payload)
            )
            return {
                'status': 'success',
                'status_code': response['StatusCode'],
                'message': 'Async processing triggered'
            }

        # Mock mode: process synchronously and log the result
        result = self._mock_process(self.function_name, payload)
        self._mock_invocations.append({
            'id': str(uuid.uuid4()),
            'function': self.function_name,
            'payload': payload,
            'result': result,
            'async': True,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        return {
            'status': 'success',
            'message': 'Mock: async processing simulated',
            'payload': result
        }

    def _mock_process(self, function_name, payload):
        """
        Simulate Lambda function processing locally.
        Provides realistic classification results based on incident data.
        """
        action = payload.get('action', 'unknown')

        if action == 'classify':
            incident = payload.get('incident', {})
            category = incident.get('category', 'other').lower()
            # Severity mapping based on category
            severity_map = {
                'assault': 'critical',
                'robbery': 'critical',
                'theft': 'high',
                'burglary': 'high',
                'vandalism': 'medium',
                'suspicious_activity': 'medium',
                'noise_complaint': 'low',
                'parking': 'low',
                'other': 'medium'
            }
            severity = severity_map.get(category, 'medium')
            priority_map = {'critical': 95, 'high': 75, 'medium': 50, 'low': 25}
            return {
                'severity': severity,
                'priority_score': priority_map.get(severity, 50),
                'auto_escalate': severity in ('critical', 'high'),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }

        if action == 'full_process':
            return {
                'incident_id': payload.get('incident_id'),
                'notifications_sent': 3,
                'analytics_updated': True,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }

        return {'action': action, 'result': 'processed'}

    def get_invocation_log(self):
        """Return the list of mock Lambda invocations (development only)."""
        return self._mock_invocations

    def get_status(self):
        """Return the current status of the Lambda service for health checks."""
        if self.use_aws:
            try:
                response = self.client.get_function(FunctionName=self.function_name)
                return {
                    'service': 'AWS Lambda',
                    'status': 'connected',
                    'mode': 'production',
                    'function': self.function_name,
                    'region': self.region
                }
            except Exception as e:
                return {
                    'service': 'AWS Lambda',
                    'status': 'error',
                    'mode': 'production',
                    'error': str(e)
                }
        return {
            'service': 'AWS Lambda',
            'status': 'mock',
            'mode': 'development',
            'function': self.function_name,
            'invocations': len(self._mock_invocations)
        }
