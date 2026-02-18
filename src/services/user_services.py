from sqlmodel import select
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from src.db.models import User
from src.db.accessor.schemas.user import Signup,SignupResponse
from src.utils.auth import generate_password_hash


class UserService:

    async def get_user_by_email(
        self,
        email: EmailStr,
        session: AsyncSession
    ) -> User :
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        user_id:UUID,
        session: AsyncSession
    ) -> User :
        return await session.get(User, user_id)

    async def user_exists(
        self,
        email: EmailStr,
        session: AsyncSession
    ) -> bool:
        user = await self.get_user_by_email(email, session)
        return user is not None

    async def create_user(
        self,
        user_data: Signup,
        session: AsyncSession
    ) -> User:
        user_data_dict = user_data.model_dump()

        # extract password
        password = user_data_dict.pop("password")

        # hash password
        user_data_dict["password_hash"] = generate_password_hash(password)

        new_user = User(**user_data_dict)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user
