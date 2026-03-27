"""
Amazon SES service wrapper with mock and real implementations.
Handles email alerts to authorities and incident reporters.
Author: Adithya Reddy Madireddy
"""

import uuid
from datetime import datetime, timezone


class SESService:
    """
    Service class for interacting with Amazon Simple Email Service.
    Sends email notifications for incident reports, status updates,
    and authority alerts. In mock mode, emails are logged in memory.
    """

    def __init__(self, app=None):
        """Initialize the SES service with optional Flask app configuration."""
        self.use_aws = False
        self.region = 'eu-west-1'
        self.sender_email = 'alerts@safety-app.example.com'
        self.client = None
        self._mock_emails = []
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Configure the service from the Flask app settings."""
        self.use_aws = app.config.get('USE_AWS', False)
        self.region = app.config.get('AWS_REGION', 'eu-west-1')
        self.sender_email = app.config.get('SES_SENDER_EMAIL', 'alerts@safety-app.example.com')
        if self.use_aws:
            import boto3
            self.client = boto3.client('ses', region_name=self.region)

    def send_email(self, to_address, subject, body_text, body_html=None):
        """
        Send an email to a single recipient using SES.

        Args:
            to_address: The recipient email address.
            subject: The email subject line.
            body_text: The plain text body.
            body_html: Optional HTML body for rich formatting.
        Returns:
            Dictionary with send status and message ID.
        """
        if self.use_aws and self.client:
            body = {'Text': {'Data': body_text, 'Charset': 'UTF-8'}}
            if body_html:
                body['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}
            response = self.client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [to_address]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': body
                }
            )
            return {
                'status': 'success',
                'message_id': response['MessageId']
            }

        # Mock mode: log the email in memory
        email_record = {
            'id': str(uuid.uuid4()),
            'from': self.sender_email,
            'to': to_address,
            'subject': subject,
            'body_text': body_text,
            'body_html': body_html,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self._mock_emails.append(email_record)
        return {
            'status': 'success',
            'message': 'Mock: email sent',
            'message_id': email_record['id']
        }

    def send_incident_report_email(self, to_address, incident_title, incident_category, severity):
        """
        Send a formatted incident report notification email.
        Used when a new incident is reported to alert authorities.
        """
        subject = f'New Incident Report [{severity.upper()}]: {incident_title}'
        body_text = (
            f'A new safety incident has been reported.\n\n'
            f'Title: {incident_title}\n'
            f'Category: {incident_category}\n'
            f'Severity: {severity}\n\n'
            f'Please log in to the Safety App to review and take action.'
        )
        body_html = (
            f'<h2>New Incident Report</h2>'
            f'<p><strong>Title:</strong> {incident_title}</p>'
            f'<p><strong>Category:</strong> {incident_category}</p>'
            f'<p><strong>Severity:</strong> <span style="color:red">{severity}</span></p>'
            f'<p>Please log in to the <a href="#">Safety App</a> to review and take action.</p>'
        )
        return self.send_email(to_address, subject, body_text, body_html)

    def send_status_update_email(self, to_address, incident_title, old_status, new_status):
        """
        Send an email notifying the reporter that incident status has changed.
        """
        subject = f'Incident Update: {incident_title}'
        body_text = (
            f'Your reported incident "{incident_title}" has been updated.\n\n'
            f'Previous status: {old_status}\n'
            f'New status: {new_status}\n\n'
            f'Check the Safety App for more details.'
        )
        return self.send_email(to_address, subject, body_text)

    def get_email_log(self):
        """Return the list of mock emails sent (development only)."""
        return self._mock_emails

    def get_status(self):
        """Return the current status of the SES service for health checks."""
        if self.use_aws:
            try:
                response = self.client.get_send_quota()
                return {
                    'service': 'Amazon SES',
                    'status': 'connected',
                    'mode': 'production',
                    'region': self.region,
                    'max_send_rate': response.get('MaxSendRate', 0)
                }
            except Exception as e:
                return {
                    'service': 'Amazon SES',
                    'status': 'error',
                    'mode': 'production',
                    'error': str(e)
                }
        return {
            'service': 'Amazon SES',
            'status': 'mock',
            'mode': 'development',
            'emails_sent': len(self._mock_emails),
            'sender': self.sender_email
        }
