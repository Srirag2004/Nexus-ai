"""add user authentication and user-scoped run history

Revision ID: 20260829_0002
Revises: 20260829_0001
"""

from alembic import op
import sqlalchemy as sa

revision = "20260829_0002"
down_revision = "20260829_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.add_column("agent_runs", sa.Column("user_id", sa.UUID(), nullable=True))
    op.add_column("evaluation_runs", sa.Column("user_id", sa.UUID(), nullable=True))
    op.create_index("ix_agent_runs_user_id", "agent_runs", ["user_id"])
    op.create_index("ix_evaluation_runs_user_id", "evaluation_runs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_evaluation_runs_user_id", table_name="evaluation_runs")
    op.drop_index("ix_agent_runs_user_id", table_name="agent_runs")
    op.drop_column("evaluation_runs", "user_id")
    op.drop_column("agent_runs", "user_id")
    op.drop_column("users", "password_hash")
