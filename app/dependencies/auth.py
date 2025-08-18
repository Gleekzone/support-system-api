from fastapi import HTTPException

def check_user_roles(current_user: dict, allowed_groups: list):
    user_groups = current_user.get("cognito:groups", [])
    if not any(g in allowed_groups for g in user_groups):
        raise HTTPException(status_code=403, detail="User not authorized")
