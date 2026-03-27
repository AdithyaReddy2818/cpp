"""
Flask application factory for the Neighbourhood Safety Incident Reporting App.
Initializes the app, database, CORS, AWS services, and registers all route blueprints.
Author: Adithya Reddy Madireddy
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

from config import config_by_name
from models.database import init_db
from routes.incident_routes import incident_bp
from routes.user_routes import user_bp
from routes.comment_routes import comment_bp
from routes.neighbourhood_routes import neighbourhood_bp
from routes.aws_routes import aws_bp, init_aws_routes
from services.dynamodb_service import DynamoDBService
from services.s3_service import S3Service
from services.sns_service import SNSService
from services.location_service import LocationService
from services.ses_service import SESService
from services.lambda_service import LambdaService


def create_app(config_name=None):
    """
    Application factory function that creates and configures a Flask app.

    Args:
        config_name: The configuration environment name.
                     Options are 'development', 'testing', 'production'.
                     Defaults to the FLASK_ENV environment variable or 'development'.
    Returns:
        A configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Enable CORS for all routes so the React frontend can communicate
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize the SQLite/SQLAlchemy database
    init_db(app)

    # Initialize all AWS service wrappers
    dynamodb_svc = DynamoDBService(app)
    s3_svc = S3Service(app)
    sns_svc = SNSService(app)
    location_svc = LocationService(app)
    ses_svc = SESService(app)
    lambda_svc = LambdaService(app)

    # Inject service instances into the AWS routes module
    init_aws_routes(dynamodb_svc, s3_svc, sns_svc, location_svc, ses_svc, lambda_svc)

    # Register all route blueprints with the application
    app.register_blueprint(incident_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(neighbourhood_bp)
    app.register_blueprint(aws_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Root health check endpoint to verify the API is running."""
        return jsonify({
            'status': 'healthy',
            'application': 'Neighbourhood Safety Incident Reporting App',
            'version': '1.0.0',
            'author': 'Adithya Reddy Madireddy'
        }), 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002, debug=True)
