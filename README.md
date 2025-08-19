# Support System API

A Proof of Concept (POC) REST API for a support ticket system. This API allows customers to create, retrieve, and manage support tickets via a web interface. The application is built using **FastAPI**, **PostgreSQL**, and deployed on **AWS Lambda** with **API Gateway**.

---

## Features

- **User Management**: Create, retrieve, and deactivate users.
- **Support Tickets**: Create, retrieve, and update support tickets.
- **AWS Integration**: Uses AWS services like Lambda, RDS (PostgreSQL), S3, and SQS.
- **Infrastructure as Code**: Terraform is used to provision AWS resources.

---

## Project Structure

```plaintext
app/
├── routes/          # API route definitions
├── schemas/         # Pydantic models for request/response validation
├── services/        # Business logic and service integrations
├── dependencies/    # Dependency injection for FastAPI
common/
├── db.py            # Database connection and ORM setup
├── logger.py        # Logging configuration
infra-tf/            # Terraform configuration for AWS infrastructure
tests/               # Unit and integration tests
```

## Prerequisites

- Python: >= 3.12
- Poetry: Dependency management
- Docker: For local development and testing
- Terraform: >= 1.5.0 for infrastructure provisioning

## Setup Instructions

1. ### Clone the Repository

```bash
git clone <repository-url>
cd support-system-api
```

2. ### Install Dependencies

```bash
 poetry install 
 ```

3. ### Run the API Locally
```bash
 uvicorn app.main:app --reload 
 ```

The API will be available at http://127.0.0.1:8000.

4. ### Run Test
```bash
 pytest
 ```

5. ### Deploy to AWS

1. Configure AWS credentials:

```bash
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=<your-region>
```

2. Provision infrastructure with Terraform:
```bash
cd infra-tf
terraform init
terraform apply
```
3. Build and push the Docker image:
```bash
docker build -t <ecr-repo-url>:latest -f docker/api.Dockerfile .
docker push <ecr-repo-url>:latest
```

### API Endpoints


### Assumptions and Design Decisions

1. Authentication: JWT-based authentication is used for protected endpoints.

2. Database: PostgreSQL is used as the primary database, hosted on AWS RDS.

3. Infrastructure: The application is designed to run serverlessly on AWS Lambda with API Gateway.

4. Error Handling: Standardized error responses are returned for invalid requests.

5. Scalability: SQS is used for asynchronous processing of bulk ticket uploads.

6. CI/CD: GitHub Actions is used for automating testing, linting, and deployment workflows to ensure code quality and streamline the deployment process.

### Testing

1. Unit Tests: Located in the tests directory. Run with pytest.

2. Integration Tests: Test interactions with external services like AWS S3 and RDS.


### Infrastructure

The infrastructure is provisioned using Terraform and includes:

- **AWS Lambda**: Hosts the FastAPI application.
- **API Gateway**: Exposes the API endpoints.
- **RDS (PostgreSQL)**: Stores user and ticket data.
- **S3**: Used for file storage.
- **SQS**: Handles bulk ticket processing.
- **CloudWatch**: Monitors application logs, metrics, and performance for debugging and operational insights.


### Example Deployment

- **API Gateway URL**: https://<api-id>.execute-api.<region>.amazonaws.com
- **RDS Endpoint**: <rds-endpoint>
- **S3 Bucket**: <bucket-name>
- **Cognito User Pool ID**: <user-pool-id>

### API Documentation

The API endpoints and their respective request/response JSON payloads can be explored using the following tools:

- **Swagger URL**: [Swagger Documentation](http://127.0.0.1:8000/docs)
- **ReDoc URL**: [ReDoc Documentation](http://127.0.0.1:8000/redoc)

Both provide an interactive interface to test and view all available endpoints.

### License
```bash
This project is licensed under the MIT License. 
```

