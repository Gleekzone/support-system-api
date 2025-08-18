import os

# Congnito configuration
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:port/dbname")

# S3 configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# SQS configuration
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
