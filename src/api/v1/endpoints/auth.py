from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
import time
from datetime import timedelta
from src.db.accessor.schemas.user import Login, Signup, SignupResponse, UserResponse
from src.db.database import get_session
from src.services.auth_services import AuthService
from src.services.user_services import UserService
from src.utils.auth import verify_password, create_access_token, decode_token, REFRESH_TOKEN_EXPIRY
from src.core.redis import redis_client
from src.api.v1.dependencies import get_current_user, AccessTokenBearer, RefreshTokenBearer

router = APIRouter(prefix="/auth", tags=["Auth"])

auth_service = AuthService()
user_service = UserService()


# ---------------- REGISTER ----------------
@router.post(
    "/register",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: Signup,
    session: AsyncSession = Depends(get_session)
):
    return await user_service.create_user(user_data, session)


# ---------------- LOGIN ----------------
@router.post("/login")
async def login_users(
    login_data: Login,
    session: AsyncSession = Depends(get_session)
):
    user = await user_service.get_user_by_email(login_data.email, session)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Email Or Password"
        )

    # Create access token
    access_token = create_access_token(
        user_data={"email": user.email, "user_uid": str(user.uid)}
    )

    # Create refresh token
    refresh_token = create_access_token(
        user_data={"email": user.email, "user_uid": str(user.uid)},
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )

    return JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"email": user.email, "uid": str(user.uid)},
        }
    )


# ---------------- ME ----------------
@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    """
    Returns the current logged-in user
    """
    return current_user


# ---------------- LOGOUT ----------------
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token_details: dict = Depends(AccessTokenBearer())):
    """
    Logout by blacklisting the current access token in Redis
    """
    jti = token_details.get("jti")
    exp = token_details.get("exp")

    if not jti or not exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload"
        )

    ttl = int(exp - time.time())
    if ttl > 0:
        redis_client.setex(jti, ttl, "revoked")  # remove await

    return {"message": "Logged out successfully"}


# ---------------- REFRESH TOKEN ----------------
@router.post("/refresh")
async def refresh_token(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Generate a new access token using a valid refresh token
    """
    payload_user = token_details.get("user")
    if not payload_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    new_access_token = create_access_token(
        user_data={"email": payload_user["email"], "user_uid": payload_user["user_uid"]}
    )

    return {"access_token": new_access_token}
