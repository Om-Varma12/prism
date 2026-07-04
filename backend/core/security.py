from fastapi import Request

def require_role(roles: list[str]):
    """
    FastAPI dependency factory that checks if the request user has one of the allowed roles.
    STUB: For local development, this returns a dummy user context without verifying cookies.
    """
    def dependency(request: Request):
        return {"role": "investigator", "user_id": "dev_user"}
    return dependency
