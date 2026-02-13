from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from src.services.auth_services import AuthService
from src.db.session import get_session
from src.db.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

auth_service = AuthService()


# ======================= LOGIN =======================

@router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """
    Login user and return access token
    """
    return await auth_service.login(
        email=form_data.username,
        password=form_data.password,
        session=session
    )


# ======================= CURRENT USER =======================

@router.get(
    "/me",
    response_model=User,
    status_code=status.HTTP_200_OK
)
async def get_current_user(
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get logged-in user details
    """
    return current_user
