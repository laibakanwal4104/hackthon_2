"""
FastAPI dependencies for authentication and authorization.
Extracts and validates JWT tokens from requests.
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from src.auth.jwt import verify_token


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Extract and verify JWT token from Authorization header.
    Returns the decoded token payload with user information.

    Args:
        authorization: Authorization header value (Bearer <token>)

    Returns:
        Decoded token payload containing user_id and email

        
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def verify_user_access(
    user_id: int,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify that the authenticated user matches the requested user_id.
    Prevents users from accessing other users' resources.

    Args:
        user_id: User ID from the request path
        current_user: Current authenticated user from JWT token

    Returns:
        Current user payload if authorized

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    token_user_id = current_user.get("sub")

    # Convert to int for comparison
    try:
        token_user_id = int(token_user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    return current_user
