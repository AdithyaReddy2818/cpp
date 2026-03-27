"""
Configuration module for the Neighbourhood Safety Incident Reporting App.
Provides separate configurations for development, testing, and production environments.
Author: Adithya Reddy Madireddy
"""

import os

class BaseConfig:
    """Base configuration shared across all environments."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'neighbourhood-safety-dev-key-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_AWS = os.environ.get('USE_AWS', 'False').lower() == 'true'
    AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-1')

    # AWS Service configuration
    DYNAMODB_TABLE_PREFIX = os.environ.get('DYNAMODB_TABLE_PREFIX', 'safety-app-')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'safety-incident-photos')
    SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
    SES_SENDER_EMAIL = os.environ.get('SES_SENDER_EMAIL', 'alerts@safety-app.example.com')
    LOCATION_INDEX_NAME = os.environ.get('LOCATION_INDEX_NAME', 'safety-app-place-index')
    LAMBDA_FUNCTION_NAME = os.environ.get('LAMBDA_FUNCTION_NAME', 'safety-incident-processor')


class DevelopmentConfig(BaseConfig):
    """Development configuration using SQLite and mock AWS services."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///safety_incidents_dev.db'
    )
    USE_AWS = False


class TestingConfig(BaseConfig):
    """Testing configuration using an in-memory SQLite database."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    USE_AWS = False


class ProductionConfig(BaseConfig):
    """Production configuration using DynamoDB and real AWS services."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///safety_incidents_prod.db'
    )
    USE_AWS = os.environ.get('USE_AWS', 'True').lower() == 'true'


# Mapping of environment names to config classes for easy lookup
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
