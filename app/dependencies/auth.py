from fastapi import HTTPException

# auth.py
import logging
from fastapi import HTTPException
import boto3
from botocore.exceptions import ClientError
from common.config import COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID, AWS_REGION

logger = logging.getLogger(__name__)

class CognitoClient:

    def __init__(self):
        self.client = boto3.client("cognito-idp", region_name=AWS_REGION)
        self.userPoolId = COGNITO_USER_POOL_ID
        self.client_id = COGNITO_CLIENT_ID

    def authenticate(self, username: str, password: str):
        try:
            resp = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password}
            )
            return resp["AuthenticationResult"]
        except ClientError as e:
            raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
    logger.info("Auth initialized.")



def check_user_roles(current_user: dict, allowed_groups: list):
    user_groups = current_user.get("cognito:groups", [])
    if not any(g in allowed_groups for g in user_groups):
        raise HTTPException(status_code=403, detail="User not authorized")
