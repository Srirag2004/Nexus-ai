# Production Deployment

Deploy NEXUS as two separate environments, each with three managed services:

- Web: Vercel (Next.js)
- API: Railway (Docker/FastAPI)
- Database: Neon PostgreSQL

Use completely separate services and databases for QA and Production. Never point QA at the production database.

| Environment | Purpose | Web URL | API URL | Database |
| --- | --- | --- | --- | --- |
| QA | Invited-user testing and release validation | `nexus-qa.vercel.app` | `nexus-api-qa.railway.app` | `nexus-qa` |
| Production | Public, real-user application | `app.yourdomain.com` | `api.yourdomain.com` | `nexus-production` |

## 1. Create QA first

Create a Neon PostgreSQL database named `nexus-qa`. Copy its pooled connection string and create two URLs from it:

```text
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST/DATABASE?ssl=require
SYNC_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

Use the same host, user, password, and database in both values. Only the driver prefix and SSL parameter differ.

## 2. Deploy the QA API

Create a Railway service named `nexus-api-qa` from this Git repository. Set its root directory to `apps/api` and let Railway build the included `Dockerfile`.

Set the following Railway variables:

```text
APP_ENV=qa
DATABASE_URL=<async PostgreSQL URL>
SYNC_DATABASE_URL=<sync PostgreSQL URL>
AI_PROVIDER=openai
OPENAI_API_KEY=<server-only OpenAI key>
OPENAI_MODEL=gpt-5
AUTH_SECRET=<long random secret>
AUTH_TOKEN_HOURS=168
ALLOWED_ORIGINS=https://YOUR-QA-VERCEL-DOMAIN.vercel.app
MAX_UPLOAD_SIZE_MB=10
```

## OAuth sign-in and GitHub connection

Google and GitHub OAuth must be configured in their provider dashboards before deploying this feature. In Railway, add:

```text
FRONTEND_URL=https://YOUR-VERCEL-DOMAIN.vercel.app
BACKEND_URL=https://YOUR-RAILWAY-DOMAIN.up.railway.app
GOOGLE_OAUTH_CLIENT_ID=<Google OAuth web client id>
GOOGLE_OAUTH_CLIENT_SECRET=<Google OAuth web client secret>
GITHUB_OAUTH_CLIENT_ID=<GitHub OAuth app client id>
GITHUB_OAUTH_CLIENT_SECRET=<GitHub OAuth app client secret>
```

Create web OAuth applications with these exact callback URLs:

```text
Google: https://YOUR-RAILWAY-DOMAIN.up.railway.app/api/v1/auth/oauth/google/callback
GitHub: https://YOUR-RAILWAY-DOMAIN.up.railway.app/api/v1/auth/oauth/github/callback
```

GitHub connection requests `repo` permission so a user can choose private repositories. Explain this clearly to users and never expose the OAuth client secret or their access token in Vercel/browser variables.

For QA without OpenAI credits, Gemini can be used instead:

```text
AI_PROVIDER=gemini
GEMINI_API_KEY=<server-only Gemini key>
GEMINI_MODEL=gemini-3.6-flash
```

Use only one live provider at a time. Keep provider keys in Railway and never expose them in Vercel or browser code.

Generate `AUTH_SECRET` with:

```bash
openssl rand -hex 32
```

The API Docker image runs `alembic upgrade head` automatically before starting. Check the Railway deployment log for `Running upgrade` to confirm it completed.

Copy the public API URL Railway assigns, for example `https://nexus-api-production.up.railway.app`.

## 3. Deploy the QA web app

Import the same Git repository into Vercel as a project named `nexus-qa`. Set its root directory to `apps/web`.

Set this Vercel environment variable for Production, Preview, and Development:

```text
NEXT_PUBLIC_API_URL=https://YOUR-QA-RAILWAY-API-DOMAIN
```

Redeploy after setting it. `NEXT_PUBLIC_API_URL` is embedded while Next.js builds, so changing it requires a rebuild.

## 4. Test QA and promote to production

Create a few QA accounts and test:

- Sign-up, sign-in, and account separation
- Conversation history creates, refreshes, reopens, and deletes correctly
- A document uploaded by one account cannot be seen by another
- Live OpenAI replies work with the QA key
- GitHub and career workflows handle invalid input without exposing errors or secrets

When QA is approved, deploy the same commit to separate Production services: `nexus-api-production`, `nexus-production`, and a new `nexus-production` Neon database. Use the exact same variables, but change:

```text
APP_ENV=production
DATABASE_URL=<production database URL>
SYNC_DATABASE_URL=<production database URL>
AUTH_SECRET=<new, unique production secret>
OPENAI_API_KEY=<production key or project>
ALLOWED_ORIGINS=https://YOUR-PRODUCTION-WEB-DOMAIN
NEXT_PUBLIC_API_URL=https://YOUR-PRODUCTION-API-DOMAIN
```

The production API Docker image runs migrations on each deploy. Deploy QA first, verify its migration log, then deploy the same commit to production.

## Production checks

- Keep `OPENAI_API_KEY` only in Railway. Never add it to Vercel or browser code.
- Keep `AUTH_SECRET` private and unique for each environment.
- Use HTTPS domains only; Vercel, Railway, and Neon provide this by default.
- Back up the Neon database before destructive schema changes.
- The API sends `store=False` with Responses API calls to avoid creating retrievable response state through the API. OpenAI still retains abuse-monitoring logs according to its data controls.
- Add email verification, password reset, rate limiting, and an HTTP-only cookie session strategy before handling sensitive public-user data at scale.
