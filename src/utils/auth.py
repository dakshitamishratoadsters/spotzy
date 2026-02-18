from passlib.context import CryptContext
from jose import jwt ,JWTError
import uuid
from datetime import datetime, timedelta
import logging
from src.core.config import Config

passwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated ="auto"
)

# Token expiry constants
ACCESS_TOKEN_EXPIRY = 60  # minutes
REFRESH_TOKEN_EXPIRY = 7  # days

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ================= PASSWORD FUNCTIONS =================
def generate_password_hash(password: str) -> str:
    return passwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return passwd_context.verify(password, hashed)


# ================= JWT FUNCTIONS =================
def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    expire_time = datetime.utcnow() + (expiry if expiry else timedelta(minutes=60))
    payload = {
        "user": user_data,
        "exp": expire_time,
        "jti": str(uuid.uuid4()),
        "refresh": refresh
    }

    token = jwt.encode(
        claims=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    return token


def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(
            token,  # just positional
            Config.JWT_SECRET,  # key
            algorithms=[Config.JWT_ALGORITHM]
        )
        print(f"Decoded token data: {token_data}")  # optional debug
        return token_data
    except JWTError as jwte:
        logging.exception("JWT decode error:", exc_info=jwte)
        return None
    except Exception as e:
        logging.exception("Unexpected error decoding token:", exc_info=e)
        return None