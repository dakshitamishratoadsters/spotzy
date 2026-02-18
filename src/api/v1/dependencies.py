from typing import Any, List
from fastapi import Depends, Request, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.services.auth_services import AuthService
from src.services.user_services import UserService
from src.db.database import get_session
from src.core.redis import redis_client
from src.utils.auth import decode_token
from src.db.accessor.schemas.user import UserResponse

auth_service = AuthService()


# ---------------- Base Token Class ----------------
class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials
        token_data = decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "This token is invalid or expired",
                        "resolution": "Please get a new token"}
            )

        # Check blacklist in Redis
        jti = token_data.get("jti")
        if jti and  redis_client.get(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This token has been revoked"
            )

        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data: dict):
        """Override in child class to distinguish access vs refresh"""
        raise NotImplementedError("Please override this method in child classes")


# ---------------- Access Token ----------------
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token"
            )


# ---------------- Refresh Token ----------------
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token"
            )


# ---------------- Get Current User ----------------
async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    """
    Fetch user object from DB using email in token.
    """
    user_email = token_details["user"]["email"]
    user_service = UserService()
    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


# ---------------- Role Checker ----------------
class RoleChecker:
    """
    Example usage:
        admin_only = RoleChecker(["admin"])
        moderator_only = RoleChecker(["moderator", "admin"])
    """
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Any = Depends(get_current_user)) -> bool:
        if current_user.role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action"
        )
