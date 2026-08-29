from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.db.models.entities import User
from app.db.session import get_db
from app.schemas.auth import AuthResponse, SignInRequest, SignUpRequest, UserResponse

router = APIRouter()


def user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, display_name=user.display_name)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignUpRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    email = payload.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="An account already exists for this email")
    user = User(email=email, display_name=payload.display_name.strip(), password_hash=hash_password(payload.password))
    db.add(user); await db.commit(); await db.refresh(user)
    return AuthResponse(access_token=create_access_token(user.id), user=user_response(user))


@router.post("/signin", response_model=AuthResponse)
async def signin(payload: SignInRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    result = await db.execute(select(User).where(User.email == payload.email.strip().lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return AuthResponse(access_token=create_access_token(user.id), user=user_response(user))


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return user_response(user)
