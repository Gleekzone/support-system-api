from fastapi import HTTPException, Request

def get_current_user(event: dict = None, request: Request = None):
    """ Extracts the current user from the event context."""
    if event is None and request is not None:
        event = getattr(request.scope.get("aws.event"), "copy", lambda: {})()

    if not isinstance(event, dict):
        raise HTTPException(status_code=400, detail="Invalid event payload: not a dictionary")

    request_context = event.get("requestContext") or {}
    if request_context is None:
        raise HTTPException(status_code=401, detail="Unauthorized: missing requestContext")

    authorizer = request_context.get("authorizer") or {}
    if authorizer is None:
        raise HTTPException(status_code=401, detail="Unauthorized: missing authorizer")

    claims = authorizer.get("claims") or {}
    if not claims:
        raise HTTPException(status_code=401, detail="Unauthorized: missing claims")

    return claims
