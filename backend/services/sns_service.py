"""
Amazon SNS service wrapper with mock and real implementations.
Handles push notifications to residents about nearby incidents.
Author: Adithya Reddy Madireddy
"""

import uuid
from datetime import datetime, timezone


class SNSService:
    """
    Service class for interacting with Amazon Simple Notification Service.
    Sends push notifications and SMS alerts to residents about incidents.
    In mock mode, notifications are logged in memory.
    """

    def __init__(self, app=None):
        """Initialize the SNS service with optional Flask app configuration."""
        self.use_aws = False
        self.region = 'eu-west-1'
        self.topic_arn = ''
        self.client = None
        self._mock_notifications = []
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Configure the service from the Flask app settings."""
        self.use_aws = app.config.get('USE_AWS', False)
        self.region = app.config.get('AWS_REGION', 'eu-west-1')
        self.topic_arn = app.config.get('SNS_TOPIC_ARN', '')
        if self.use_aws:
            import boto3
            self.client = boto3.client('sns', region_name=self.region)

    def publish_notification(self, subject, message, target_arn=None):
        """
        Publish a notification to an SNS topic or a specific target.
        Used to alert residents about new or updated incidents nearby.

        Args:
            subject: The notification subject line.
            message: The notification body text.
            target_arn: Optional specific target ARN. Uses default topic if None.
        Returns:
            Dictionary with publish status and message ID.
        """
        arn = target_arn or self.topic_arn
        if self.use_aws and self.client:
            response = self.client.publish(
                TopicArn=arn,
                Subject=subject,
                Message=message
            )
            return {
                'status': 'success',
                'message_id': response['MessageId']
            }

        # Mock mode: log the notification in memory
        notification = {
            'id': str(uuid.uuid4()),
            'subject': subject,
            'message': message,
            'target_arn': arn,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self._mock_notifications.append(notification)
        return {
            'status': 'success',
            'message': 'Mock: notification published',
            'message_id': notification['id']
        }

    def subscribe(self, protocol, endpoint):
        """
        Subscribe an endpoint to the SNS topic for notifications.

        Args:
            protocol: The subscription protocol (email, sms, http, etc.).
            endpoint: The endpoint address (email address, phone number, URL).
        Returns:
            Dictionary with subscription status.
        """
        if self.use_aws and self.client:
            response = self.client.subscribe(
                TopicArn=self.topic_arn,
                Protocol=protocol,
                Endpoint=endpoint
            )
            return {
                'status': 'success',
                'subscription_arn': response['SubscriptionArn']
            }

        # Mock mode: simulate subscription
        return {
            'status': 'success',
            'message': f'Mock: subscribed {endpoint} via {protocol}',
            'subscription_arn': f'arn:aws:sns:{self.region}:mock:safety-alerts:{uuid.uuid4().hex[:8]}'
        }

    def notify_neighbourhood(self, neighbourhood_name, incident_title, severity):
        """
        Send a notification about an incident to all subscribers of a neighbourhood.
        Constructs a formatted message with incident details and severity.
        """
        subject = f'Safety Alert [{severity.upper()}]: {neighbourhood_name}'
        message = (
            f'A new incident has been reported in {neighbourhood_name}.\n\n'
            f'Incident: {incident_title}\n'
            f'Severity: {severity}\n\n'
            f'Please check the Safety App for more details and stay alert.'
        )
        return self.publish_notification(subject, message)

    def get_notifications_log(self):
        """Return the list of mock notifications sent (development only)."""
        return self._mock_notifications

    def get_status(self):
        """Return the current status of the SNS service for health checks."""
        if self.use_aws:
            try:
                response = self.client.get_topic_attributes(TopicArn=self.topic_arn)
                return {
                    'service': 'Amazon SNS',
                    'status': 'connected',
                    'mode': 'production',
                    'topic_arn': self.topic_arn,
                    'region': self.region
                }
            except Exception as e:
                return {
                    'service': 'Amazon SNS',
                    'status': 'error',
                    'mode': 'production',
                    'error': str(e)
                }
        return {
            'service': 'Amazon SNS',
            'status': 'mock',
            'mode': 'development',
            'notifications_sent': len(self._mock_notifications)
        }
