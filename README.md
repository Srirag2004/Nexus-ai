# NEXUS AI

NEXUS AI is a portfolio-grade AI engineering workspace built as a Next.js frontend and FastAPI backend. It combines persistent conversations, document retrieval, memory, GitHub repository analysis, career-fit heuristics, and an agent-oriented orchestration layer behind a command-center UI.

## Current Status

This repository now contains a working full-stack foundation with:

- FastAPI API with versioned routes under `/api/v1`
- AI provider abstraction with `mock` and `openai` providers
- persistent data models for conversations, messages, documents, memories, repositories, career analyses, agent runs, and evaluation runs
- document ingestion for TXT, Markdown, and PDF
- simple chunking and similarity retrieval with source citations
- memory CRUD plus lightweight memory extraction/retrieval
- GitHub repository ingestion through the GitHub REST API
- heuristic career analysis endpoint
- agent workflow shell for planner, researcher, developer, career, and reviewer stages
- Next.js dashboard and product pages for chat, knowledge, GitHub, career, memory, agents, and settings
- Dockerfiles, `docker-compose.yml`, Alembic migration scaffolding, and GitHub Actions

## Architecture

- Frontend: Next.js App Router, TypeScript, Tailwind CSS
- Backend: FastAPI, Pydantic Settings, SQLAlchemy 2.x, Alembic
- AI: provider abstraction with mock-first local behavior and OpenAI Responses API support
- Retrieval: document chunking plus bounded semantic ranking
- Agents: lightweight orchestrator flow modeled after planner/researcher/developer/career/reviewer responsibilities
- Storage: SQLAlchemy models designed for PostgreSQL, with SQLite-friendly defaults for local development

See `docs/ARCHITECTURE.md`, `docs/RAG.md`, `docs/AGENTS.md`, and `docs/DATABASE.md`.

## Local Setup

### Backend

1. Use Python 3.11+.
2. Install dependencies from `apps/api/requirements.txt`.
3. Copy `.env.example` to `.env` and adjust values.
4. Run the API from `apps/api`:

```bash
uvicorn app.main:app --reload
```

### Frontend

1. Use Node.js 22+.
2. From `apps/web`, install dependencies:

```bash
npm install
```

3. Start the app:

```bash
npm run dev
```

## Docker

Run the full stack with:

```bash
docker compose up --build
```

## Testing

Frontend:

```bash
cd apps/web
npm run lint
npm run typecheck
npm run build
```

Backend:

```bash
cd apps/api
pytest
```

## Limitations

- Retrieval currently uses application-side similarity scoring over stored embeddings rather than verified pgvector queries.
- The agent graph is intentionally lightweight and should be deepened with true LangGraph transitions and richer tool logging.
- Local backend package installation was blocked in this workspace by Windows filesystem permissions, so backend runtime verification should be repeated in a clean Python environment.
- Frontend production build is currently blocked in this workspace by a Windows `spawn EPERM` issue during Next.js compilation.
