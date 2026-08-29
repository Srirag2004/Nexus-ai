# Architecture

NEXUS AI uses a two-app monorepo:

- `apps/web`: Next.js command-center UI
- `apps/api`: FastAPI orchestration, persistence, and integrations

## Request Flow

1. The web client sends requests to the FastAPI API.
2. The API routes to service modules by domain.
3. Chat requests collect bounded memory and document context.
4. The agent workflow annotates a plan for the response.
5. The active AI provider generates the final answer.
6. The conversation, messages, and agent run are stored.

