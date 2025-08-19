import os
from dotenv import load_dotenv

# Carga variables del .env
load_dotenv()

# Congnito configuration
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:pass@host.docker.internal:5432/mydb")

# S3 configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# SQS configuration
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")


LOCALSTACK_HOST = os.getenv("LOCALSTACK_HOST", "localhost")