import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Copy backend/.env.example to backend/.env and fill it in.")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prepare(password: str) -> bytes:
    # bcrypt only looks at the first 72 bytes of the password.
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return pwd_context.hash(_prepare(password))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_prepare(plain), hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
