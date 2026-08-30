from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.core.config import get_settings
from app.db.models.entities import User
from app.db.session import get_db
from app.schemas.auth import AuthResponse, SignInRequest, SignUpRequest, UserResponse
from app.services.oauth import OAuthService

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


@router.get("/oauth/{provider}/start")
async def oauth_start(provider: str, db: AsyncSession = Depends(get_db)) -> RedirectResponse:
    try:
        return RedirectResponse(OAuthService(db).authorization_url(provider))
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, code: str = Query(...), state: str = Query(...), db: AsyncSession = Depends(get_db)) -> RedirectResponse:
    settings = get_settings()
    try:
        user = await OAuthService(db).authenticate(provider, code, state)
        # Vercel reliably delivers query parameters to the client app, where AuthGate immediately stores and removes this temporary value.
        return RedirectResponse(f"{settings.frontend_url.rstrip('/')}/?oauth_token={quote(create_access_token(user.id))}")
    except Exception:
        return RedirectResponse(f"{settings.frontend_url.rstrip('/')}/?oauth_error={quote('OAuth sign-in failed. Please try again.')}")
