from datetime import timedelta
from jose import JWTError
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.services.user_services import UserService
from src.utils.auth import (
    verify_password,
    create_access_token,
    decode_access_token
)
from src.db.models.user import User


ACCESS_TOKEN_EXPIRE_HOURS = 24


class AuthService:

    def __init__(self):
        self.user_service = UserService()

    # ---------------- LOGIN ----------------

    async def login(
        self,
        email: str,
        password: str,
        session: AsyncSession
    ) -> dict:

        user = await self.user_service.get_user_by_email(email, session)

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # optional but recommended
        if hasattr(user, "is_active") and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )

        access_token = create_access_token(
            data={
                "sub": str(user.uid),
                "role": user.role
            },
            expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    # ---------------- CURRENT USER ----------------

    async def get_current_user(
        self,
        token: str,
        session: AsyncSession
    ) -> User:

        try:
            payload = decode_access_token(token)
            user_id: str | None = payload.get("sub")

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        user = await session.get(User, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    # ---------------- ADMIN CHECK ----------------

    async def require_admin(
        self,
        user: User
    ) -> None:
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
