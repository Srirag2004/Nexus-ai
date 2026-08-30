import base64
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models.entities import OAuthAccount, User


class OAuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()

    def authorization_url(self, provider: str) -> str:
        client_id, _ = self._credentials(provider)
        params = {
            "client_id": client_id,
            "redirect_uri": self._callback_url(provider),
            "response_type": "code",
            "state": self._state(provider),
        }
        if provider == "google":
            params.update({"scope": "openid email profile", "access_type": "offline", "prompt": "select_account"})
            return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
        if provider == "github":
            # repo is required only because this version supports importing private repositories on consent.
            params.update({"scope": "read:user user:email repo"})
            return "https://github.com/login/oauth/authorize?" + urlencode(params)
        raise ValueError("Unsupported OAuth provider")

    async def authenticate(self, provider: str, code: str, state: str) -> User:
        self._verify_state(provider, state)
        token = await self._exchange_code(provider, code)
        profile = await self._profile(provider, token)
        result = await self.db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_account_id == profile["id"],
            )
        )
        account = result.scalar_one_or_none()
        if account:
            account.encrypted_access_token = self._encrypt(token)
            account.username = profile["username"]
            await self.db.commit()
            user = await self.db.get(User, account.user_id)
            if user is None:
                raise ValueError("OAuth account is not linked to a user")
            return user

        result = await self.db.execute(select(User).where(User.email == profile["email"]))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                email=profile["email"],
                display_name=profile["name"] or profile["username"],
                password_hash=hash_password(secrets.token_urlsafe(32)),
            )
            self.db.add(user)
            await self.db.flush()
        self.db.add(
            OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_account_id=profile["id"],
                username=profile["username"],
                encrypted_access_token=self._encrypt(token),
                scopes="read:user user:email repo" if provider == "github" else "openid email profile",
            )
        )
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def github_token_for_user(self, user_id) -> str | None:
        result = await self.db.execute(
            select(OAuthAccount).where(OAuthAccount.user_id == user_id, OAuthAccount.provider == "github")
        )
        account = result.scalar_one_or_none()
        return self._decrypt(account.encrypted_access_token) if account else None

    async def github_connected(self, user_id) -> bool:
        result = await self.db.execute(
            select(OAuthAccount.id).where(OAuthAccount.user_id == user_id, OAuthAccount.provider == "github")
        )
        return result.scalar_one_or_none() is not None

    async def _exchange_code(self, provider: str, code: str) -> str:
        client_id, client_secret = self._credentials(provider)
        payload = {"client_id": client_id, "client_secret": client_secret, "code": code, "redirect_uri": self._callback_url(provider)}
        async with httpx.AsyncClient(timeout=20.0) as client:
            if provider == "google":
                response = await client.post("https://oauth2.googleapis.com/token", data={**payload, "grant_type": "authorization_code"})
            else:
                response = await client.post("https://github.com/login/oauth/access_token", data=payload, headers={"Accept": "application/json"})
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise ValueError("OAuth provider did not return an access token")
        return token

    async def _profile(self, provider: str, token: str) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=20.0) as client:
            if provider == "google":
                response = await client.get("https://openidconnect.googleapis.com/v1/userinfo", headers=headers)
                response.raise_for_status()
                data = response.json()
                if not data.get("email") or not data.get("email_verified"):
                    raise ValueError("Google must provide a verified email address")
                return {"id": data["sub"], "email": data["email"].lower(), "name": data.get("name", ""), "username": data["email"].split("@", 1)[0]}
            response = await client.get("https://api.github.com/user", headers=headers)
            response.raise_for_status()
            data = response.json()
            emails = await client.get("https://api.github.com/user/emails", headers=headers)
            emails.raise_for_status()
            primary = next((item for item in emails.json() if item.get("primary") and item.get("verified")), None)
            email = primary.get("email") if primary else None
            if not email:
                raise ValueError("GitHub must provide a verified primary email address")
            return {"id": str(data["id"]), "email": email.lower(), "name": data.get("name") or "", "username": data.get("login") or email.split("@", 1)[0]}

    def _credentials(self, provider: str) -> tuple[str, str]:
        values = (
            (self.settings.google_oauth_client_id, self.settings.google_oauth_client_secret)
            if provider == "google"
            else (self.settings.github_oauth_client_id, self.settings.github_oauth_client_secret)
            if provider == "github"
            else (None, None)
        )
        if not all(values):
            raise ValueError(f"{provider.title()} OAuth is not configured yet")
        return values[0], values[1]

    def _callback_url(self, provider: str) -> str:
        return f"{self.settings.backend_url.rstrip('/')}/api/v1/auth/oauth/{provider}/callback"

    def _state(self, provider: str) -> str:
        body = base64.urlsafe_b64encode(json.dumps({"provider": provider, "exp": int(time.time()) + 600}).encode()).decode().rstrip("=")
        signature = hmac.new(self.settings.auth_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        return f"{body}.{signature}"

    def _verify_state(self, provider: str, state: str) -> None:
        try:
            body, signature = state.split(".", 1)
            expected = hmac.new(self.settings.auth_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
            payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
            if not hmac.compare_digest(signature, expected) or payload["provider"] != provider or payload["exp"] < time.time():
                raise ValueError
        except (ValueError, KeyError, json.JSONDecodeError):
            raise ValueError("OAuth request expired. Start again from NEXUS.") from None

    def _fernet(self):
        from cryptography.fernet import Fernet

        key = base64.urlsafe_b64encode(hashlib.sha256(self.settings.auth_secret.encode()).digest())
        return Fernet(key)

    def _encrypt(self, token: str) -> str:
        return self._fernet().encrypt(token.encode()).decode()

    def _decrypt(self, encrypted_token: str) -> str:
        return self._fernet().decrypt(encrypted_token.encode()).decode()
