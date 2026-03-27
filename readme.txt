================================================================================
  NEIGHBOURHOOD SAFETY INCIDENT REPORTING APP
  Author: Adithya Reddy Madireddy
  National College of Ireland - Cloud Platform Programming
================================================================================

PROJECT OVERVIEW
----------------
A cloud-native web application for reporting, tracking, and analysing
neighbourhood safety incidents. Residents can report incidents with photos
and location data, authorities can manage and resolve them, and dashboards
provide statistical insights into community safety trends.

AWS SERVICES USED (6)
---------------------
1. Amazon DynamoDB    - NoSQL database for incident and user storage
2. Amazon S3          - Object storage for incident photos and evidence
3. Amazon SNS         - Push notifications to residents about nearby incidents
4. Amazon Location    - Geocoding addresses and map-based features
5. Amazon SES         - Email alerts to authorities and reporters
6. AWS Lambda         - Async incident processing and severity classification

All services run in MOCK MODE by default (USE_AWS=False).
No AWS credentials needed for local development.

CUSTOM LIBRARY: SafeZone
------------------------
Python package with 5 OOP classes:
- IncidentClassifier  : Severity scoring, category detection, priority
- ZoneManager         : Polygon boundaries, point-in-zone, hotspots
- AlertEngine         : Radius alerts, escalation, cooldown periods
- TrendAnalyzer       : Moving averages, seasonal patterns, spike detection
- ReportGenerator     : Summary stats, markdown/text report export

DEPENDENCIES
------------
Backend (Python 3.9+):
  - Flask 3.1.0
  - Flask-SQLAlchemy 3.1.1
  - Flask-CORS 5.0.1
  - boto3 1.35.0
  - pytest 8.3.4
  - pytest-cov 6.0.0

Frontend (Node.js 18+):
  - React 18.2.0
  - react-router-dom 6.20.0
  - axios 1.6.0

SETUP AND INSTALLATION
-----------------------

1. Clone the repository:
   git clone <repository-url>
   cd Adithya

2. Install the SafeZone library:
   cd safezone
   pip install -e .
   cd ..

3. Install backend dependencies:
   cd backend
   pip install -r requirements.txt
   cd ..

4. Install frontend dependencies:
   cd frontend
   npm install
   cd ..

RUNNING THE APPLICATION
-----------------------

1. Start the backend (Terminal 1):
   cd backend
   python app.py
   The API will be available at http://localhost:5002

2. Start the frontend (Terminal 2):
   cd frontend
   npm start
   The app will be available at http://localhost:3002

3. Verify the API health:
   curl http://localhost:5002/api/health

RUNNING TESTS
-------------

Backend tests (from backend directory):
   python -m pytest tests/ -v

SafeZone library tests (from safezone directory):
   python -m pytest tests/ -v

Run all tests with coverage:
   cd backend && python -m pytest tests/ -v --cov=. --cov-report=term-missing
   cd ../safezone && python -m pytest tests/ -v --cov=safezone --cov-report=term-missing

GENERATING ARCHITECTURE DIAGRAM
--------------------------------
   cd report
   python architecture.py
   (Produces architecture_diagram.png)

PROJECT STRUCTURE
-----------------
Adithya/
  backend/          - Flask REST API (port 5002)
    app.py          - Application factory
    config.py       - Environment configurations
    models/         - SQLAlchemy database models
    routes/         - API route blueprints
    services/       - AWS service wrappers (mock + real)
    tests/          - pytest test suites
  frontend/         - React SPA (port 3002)
    src/pages/      - Page components
    src/components/ - Shared UI components
    src/services/   - API client module
  safezone/         - Custom Python library
    safezone/       - Library source code
    tests/          - Library test suites
    setup.py        - Package installation config
    pyproject.toml  - Modern package config
  report/           - IEEE LaTeX report and diagram generator
  .github/          - CI/CD GitHub Actions workflow

API ENDPOINTS
-------------
GET    /api/health                  - Health check
GET    /api/incidents               - List all incidents
POST   /api/incidents               - Create incident
GET    /api/incidents/:id           - Get incident detail
PUT    /api/incidents/:id           - Update incident
DELETE /api/incidents/:id           - Delete incident
PATCH  /api/incidents/:id/status    - Update incident status
POST   /api/incidents/:id/photos    - Add photo to incident
GET    /api/incidents/stats         - Incident statistics
GET    /api/users                   - List all users
POST   /api/users                   - Create user
GET    /api/users/:id               - Get user detail
PUT    /api/users/:id               - Update user
DELETE /api/users/:id               - Delete user
GET    /api/users/stats             - User statistics
GET    /api/comments                - List all comments
POST   /api/comments                - Create comment
GET    /api/comments/:id            - Get comment detail
PUT    /api/comments/:id            - Update comment
DELETE /api/comments/:id            - Delete comment
GET    /api/neighbourhoods          - List all neighbourhoods
POST   /api/neighbourhoods          - Create neighbourhood
GET    /api/neighbourhoods/:id      - Get neighbourhood detail
PUT    /api/neighbourhoods/:id      - Update neighbourhood
DELETE /api/neighbourhoods/:id      - Delete neighbourhood
GET    /api/neighbourhoods/stats    - Neighbourhood statistics
GET    /api/aws/status              - AWS services health
POST   /api/aws/geocode             - Geocode address
POST   /api/aws/notify              - Send SNS notification
POST   /api/aws/email               - Send SES email
POST   /api/aws/classify            - Classify incident via Lambda
POST   /api/aws/upload              - Upload file to S3

DEPLOYMENT (PRODUCTION)
-----------------------
Set the following environment variables:
  FLASK_ENV=production
  USE_AWS=True
  AWS_REGION=eu-west-1
  SECRET_KEY=<your-secret-key>
  DYNAMODB_TABLE_PREFIX=safety-app-
  S3_BUCKET_NAME=safety-incident-photos
  SNS_TOPIC_ARN=arn:aws:sns:eu-west-1:...
  SES_SENDER_EMAIL=alerts@yourdomain.com
  LOCATION_INDEX_NAME=safety-app-place-index
  LAMBDA_FUNCTION_NAME=safety-incident-processor

================================================================================
