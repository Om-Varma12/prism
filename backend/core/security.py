from fastapi import Request, HTTPException
from typing import Optional

# Valid roles in the system
VALID_ROLES = {"investigator", "analyst", "supervisor"}

# Role hierarchy (higher roles inherit lower permissions)
ROLE_HIERARCHY = {
    "supervisor": ["investigator", "analyst"],
    "analyst": ["investigator"],
    "investigator": [],
}


def get_current_user(request: Request) -> dict:
    """
    Extract user information from the request.
    
    In production, this would parse Catalyst session cookies or headers.
    For local development, returns a default user context.
    """
    # Check for Catalyst session headers (production)
    user_role = request.headers.get("X-Catalyst-Role", "investigator")
    user_id = request.headers.get("X-Catalyst-User", "dev_user")
    
    # Validate role
    if user_role not in VALID_ROLES:
        user_role = "investigator"
    
    return {"role": user_role, "user_id": user_id}


def require_role(roles: list[str]):
    """
    FastAPI dependency factory that checks if the request user has one of the allowed roles.
    
    Args:
        roles: List of allowed role names (e.g., ["analyst", "supervisor"])
        
    Returns:
        A dependency function that returns user context if authorized, raises 403 otherwise.
    """
    def dependency(request: Request):
        user = get_current_user(request)
        user_role = user["role"]
        
        # Check if user has one of the required roles
        # Also check role hierarchy - supervisors can access analyst endpoints
        has_access = False
        for required_role in roles:
            if user_role == required_role:
                has_access = True
                break
            # Check if user's role inherits the required role
            if user_role in ROLE_HIERARCHY:
                if required_role in ROLE_HIERARCHY[user_role]:
                    has_access = True
                    break
        
        if not has_access:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(roles)}. Your role: {user_role}"
            )
        
        return user
    
    return dependency
