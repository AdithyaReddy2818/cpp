# SafetyNet: Neighbourhood Safety Incident Reporting App

A cloud-based platform for reporting, tracking, and managing neighbourhood safety incidents. SafetyNet empowers communities to document safety concerns with location data and images, receive real-time notifications, and collaborate with local authorities.

## Architecture

- **Frontend** — React (Vite) single-page application hosted on Amazon S3 static website
- **Backend** — AWS Lambda function behind API Gateway (REST, regional)
- **Database** — Amazon DynamoDB (`safetyreports-prod`, on-demand capacity)
- **Storage** — Amazon S3 (`safetyreports-images-prod-adithya`) for incident images
- **Notifications** — Amazon SNS (`safetyreports-notifications`) for alert delivery
- **Shared Library** — Python package under `library/` with reusable utilities

## Project Structure

```
Adithya/
├── backend/               # Lambda function source
│   └── lambda_function.py
├── frontend/              # React + Vite application
│   ├── src/
│   └── package.json
├── library/               # Shared Python library
│   ├── setup.py
│   └── tests/
├── .github/workflows/
│   └── deploy.yml         # CI/CD pipeline
└── README.md
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) runs on every push to `main`:

1. **test-library** — Installs the shared Python library and runs pytest
2. **deploy-backend** — Provisions DynamoDB, S3, IAM, SNS, Lambda, and API Gateway
3. **deploy-frontend** — Builds the React app with the API URL and deploys to S3

### Required Secrets

| Secret                  | Description              |
|-------------------------|--------------------------|
| `AWS_ACCESS_KEY_ID`     | AWS IAM access key ID    |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret access key|

### AWS Region

All resources are deployed to **eu-west-1** (Ireland).

## Features

- Report safety incidents with title, description, category, and severity
- Upload incident images stored securely in S3
- Real-time SNS notifications for new incident reports
- JWT-based authentication for secure access
- Responsive UI for desktop and mobile devices
- Browse and filter incidents by category, severity, and location

## Getting Started

### Frontend (local development)

```bash
cd frontend
npm install
VITE_API_URL=http://localhost:3000 npm run dev
```

### Library (testing)

```bash
cd library
pip install -e .
pip install pytest
pytest tests/ -v
```

## Deployment

Push to the `main` branch to trigger automatic deployment via GitHub Actions. Ensure the required AWS secrets are configured in the repository settings.

## AWS Resources

| Resource       | Name                                  |
|----------------|---------------------------------------|
| DynamoDB Table | `safetyreports-prod`                  |
| S3 (Images)    | `safetyreports-images-prod-adithya`   |
| S3 (Frontend)  | `safetyreports-frontend-prod-adithya` |
| Lambda         | `safetyreports-api`                   |
| API Gateway    | `safetyreports-api`                   |
| SNS Topic      | `safetyreports-notifications`         |
| IAM Role       | `safetyreports-lambda-role`           |
