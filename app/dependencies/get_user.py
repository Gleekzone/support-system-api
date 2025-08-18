from fastapi import HTTPException

def get_current_user(event: dict = None):
    """ Extracts the current user from the event context."""
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    if not claims:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return claims
