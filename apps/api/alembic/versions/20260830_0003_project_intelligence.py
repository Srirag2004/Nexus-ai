"""add project intelligence workspaces

Revision ID: 20260830_0003
Revises: 20260829_0002
"""

from alembic import op
import sqlalchemy as sa


revision = "20260830_0003"
down_revision = "20260829_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("repository_id", sa.UUID(), sa.ForeignKey("github_repositories.id"), nullable=True),
        sa.Column("brief", sa.Text(), nullable=False),
        sa.Column("milestones", sa.JSON(), nullable=False),
        sa.Column("risks", sa.JSON(), nullable=False),
        sa.Column("next_steps", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"])
    op.create_table(
        "project_documents",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("document_id", sa.UUID(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "document_id", name="uq_project_document"),
    )
    op.create_index("ix_project_documents_project_id", "project_documents", ["project_id"])
    op.create_index("ix_project_documents_document_id", "project_documents", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_project_documents_document_id", table_name="project_documents")
    op.drop_index("ix_project_documents_project_id", table_name="project_documents")
    op.drop_table("project_documents")
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_table("projects")
