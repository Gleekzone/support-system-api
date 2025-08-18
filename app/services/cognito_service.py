import boto3
from fastapi import HTTPException
from app.config import COGNITO_REGION, COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID


class CognitoService:
    def __init__(self):
        self.cognito_client = boto3.client(
            'cognito-idp',
            region_name=COGNITO_REGION
        )
        self.user_pool_id = COGNITO_USER_POOL_ID
        self.client_id = COGNITO_CLIENT_ID
    
    def create_user(self, name: str, email: str, password: str):
        """Create a new user in Cognito."""
        try:
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'name', 'Value': name}
                ],
                TemporaryPassword=password,
                MessageAction="SUPPRESS" # Suppress the welcome email
            )
            return response
        except self.cognito_client.exceptions.UsernameExistsException:
            raise HTTPException(status_code=400, detail="User already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    

    def deactivate_user(self, cognito_sub: str):
        """Deactivate a user in Cognito."""
        try:
            self.cognito_client.admin_disable_user(
                UserPoolId=self.user_pool_id,
                Username=cognito_sub
            )
            return {"message": f"User {cognito_sub} has been successfully deactivated."}
        except self.cognito_client.exceptions.UserNotFoundException:
            raise HTTPException(status_code=404, detail="User not found in Cognito")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
