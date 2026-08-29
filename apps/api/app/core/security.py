import base64
import hashlib
import hmac
import json
import os
import time
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.entities import User
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return "scrypt$" + base64.urlsafe_b64encode(salt + digest).decode()


def verify_password(password: str, stored: str) -> bool:
    try:
        _, encoded = stored.split("$", 1)
        raw = base64.urlsafe_b64decode(encoded.encode())
        return hmac.compare_digest(hashlib.scrypt(password.encode(), salt=raw[:16], n=16384, r=8, p=1), raw[16:])
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    body = base64.urlsafe_b64encode(json.dumps({"sub": str(user_id), "exp": int(time.time()) + settings.auth_token_hours * 3600}).encode()).decode().rstrip("=")
    signature = hmac.new(settings.auth_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def decode_access_token(token: str) -> UUID:
    try:
        body, signature = token.split(".", 1)
        expected = hmac.new(get_settings().auth_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if int(payload["exp"]) < time.time():
            raise ValueError
        return UUID(payload["sub"])
    except (ValueError, KeyError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: AsyncSession = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue")
    user = await db.get(User, decode_access_token(credentials.credentials))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found")
    return user
