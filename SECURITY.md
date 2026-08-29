# Security

- Secrets are environment-only.
- Browser code never receives `OPENAI_API_KEY` or `GITHUB_TOKEN`.
- Uploads are size-limited and filenames are sanitized.
- CORS is explicitly configured from environment variables.

