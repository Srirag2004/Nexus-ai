"""initial schema

Revision ID: 20260829_0001
Revises:
Create Date: 2026-08-29
"""

from alembic import op
import sqlalchemy as sa


revision = "20260829_0001"
down_revision = None
branch_labels = None
depends_on = None


def _uuid_type():
    return sa.UUID() if hasattr(sa, "UUID") else sa.String(length=36)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", _uuid_type(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=True, unique=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    for table_name in [
        "conversations",
        "messages",
        "documents",
        "document_chunks",
        "memories",
        "github_repositories",
        "repository_analyses",
        "job_descriptions",
        "career_analyses",
        "agent_runs",
        "tool_invocations",
        "evaluation_runs",
    ]:
        if table_name == "conversations":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
                sa.Column("title", sa.String(length=255), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "messages":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("conversation_id", _uuid_type(), sa.ForeignKey("conversations.id"), nullable=False),
                sa.Column("role", sa.String(length=32), nullable=False),
                sa.Column("content", sa.Text(), nullable=False),
                sa.Column("sources", sa.JSON(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "documents":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
                sa.Column("filename", sa.String(length=255), nullable=False),
                sa.Column("content_type", sa.String(length=100), nullable=False),
                sa.Column("status", sa.String(length=32), nullable=False),
                sa.Column("text_content", sa.Text(), nullable=False),
                sa.Column("metadata", sa.JSON(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "document_chunks":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("document_id", _uuid_type(), sa.ForeignKey("documents.id"), nullable=False),
                sa.Column("chunk_index", sa.Integer(), nullable=False),
                sa.Column("content", sa.Text(), nullable=False),
                sa.Column("source_ref", sa.String(length=255), nullable=True),
                sa.Column("embedding", sa.JSON(), nullable=False),
                sa.Column("metadata", sa.JSON(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "memories":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
                sa.Column("category", sa.String(length=50), nullable=False),
                sa.Column("content", sa.Text(), nullable=False),
                sa.Column("importance", sa.Float(), nullable=False),
                sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
                sa.Column("embedding", sa.JSON(), nullable=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "github_repositories":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
                sa.Column("owner", sa.String(length=255), nullable=False),
                sa.Column("name", sa.String(length=255), nullable=False),
                sa.Column("url", sa.String(length=500), nullable=False),
                sa.Column("readme", sa.Text(), nullable=False),
                sa.Column("languages", sa.JSON(), nullable=False),
                sa.Column("file_index", sa.JSON(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "repository_analyses":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("repository_id", _uuid_type(), sa.ForeignKey("github_repositories.id"), nullable=False),
                sa.Column("summary", sa.Text(), nullable=False),
                sa.Column("strengths", sa.JSON(), nullable=False),
                sa.Column("issues", sa.JSON(), nullable=False),
                sa.Column("recommendations", sa.JSON(), nullable=False),
                sa.Column("architecture", sa.Text(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "job_descriptions":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
                sa.Column("title", sa.String(length=255), nullable=False),
                sa.Column("content", sa.Text(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "career_analyses":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("user_id", _uuid_type(), sa.ForeignKey("users.id"), nullable=False),
                sa.Column("resume_text", sa.Text(), nullable=False),
                sa.Column("job_description", sa.Text(), nullable=False),
                sa.Column("match_score", sa.Float(), nullable=False),
                sa.Column("matched_skills", sa.JSON(), nullable=False),
                sa.Column("missing_skills", sa.JSON(), nullable=False),
                sa.Column("recommendations", sa.JSON(), nullable=False),
                sa.Column("summary", sa.Text(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "agent_runs":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("conversation_id", _uuid_type(), sa.ForeignKey("conversations.id"), nullable=True),
                sa.Column("agent_name", sa.String(length=100), nullable=False),
                sa.Column("status", sa.String(length=32), nullable=False),
                sa.Column("input_summary", sa.Text(), nullable=False),
                sa.Column("output_summary", sa.Text(), nullable=False),
                sa.Column("duration_ms", sa.Integer(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "tool_invocations":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("agent_run_id", _uuid_type(), sa.ForeignKey("agent_runs.id"), nullable=True),
                sa.Column("tool_name", sa.String(length=100), nullable=False),
                sa.Column("status", sa.String(length=32), nullable=False),
                sa.Column("inputs", sa.JSON(), nullable=False),
                sa.Column("outputs", sa.JSON(), nullable=False),
                sa.Column("error_message", sa.Text(), nullable=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        elif table_name == "evaluation_runs":
            op.create_table(
                table_name,
                sa.Column("id", _uuid_type(), primary_key=True),
                sa.Column("evaluation_type", sa.String(length=50), nullable=False),
                sa.Column("status", sa.String(length=32), nullable=False),
                sa.Column("metrics", sa.JSON(), nullable=False),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )


def downgrade() -> None:
    for table_name in [
        "evaluation_runs",
        "tool_invocations",
        "agent_runs",
        "career_analyses",
        "job_descriptions",
        "repository_analyses",
        "github_repositories",
        "memories",
        "document_chunks",
        "documents",
        "messages",
        "conversations",
        "users",
    ]:
        op.drop_table(table_name)

