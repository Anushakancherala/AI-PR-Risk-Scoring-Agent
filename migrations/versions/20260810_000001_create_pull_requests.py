"""create pull requests table

Revision ID: 20260810_000001
Revises: 
Create Date: 2026-08-10 00:00:01.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260810_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pull_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("repository_name", sa.String(length=255), nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("base_branch", sa.String(length=255), nullable=False),
        sa.Column("head_branch", sa.String(length=255), nullable=False),
        sa.Column("head_sha", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pull_requests_id"), "pull_requests", ["id"], unique=False)
    op.create_index(op.f("ix_pull_requests_repository_id"), "pull_requests", ["repository_id"], unique=False)
    op.create_index(op.f("ix_pull_requests_repository_name"), "pull_requests", ["repository_name"], unique=False)
    op.create_index(op.f("ix_pull_requests_pr_number"), "pull_requests", ["pr_number"], unique=False)
    op.create_index(op.f("ix_pull_requests_author"), "pull_requests", ["author"], unique=False)

    op.create_table(
        "github_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("delivery_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("repository_name", sa.String(length=255), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_id"),
    )
    op.create_index(op.f("ix_github_deliveries_id"), "github_deliveries", ["id"], unique=False)
    op.create_index(op.f("ix_github_deliveries_delivery_id"), "github_deliveries", ["delivery_id"], unique=False)
    op.create_index(op.f("ix_github_deliveries_event_type"), "github_deliveries", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_github_deliveries_event_type"), table_name="github_deliveries")
    op.drop_index(op.f("ix_github_deliveries_delivery_id"), table_name="github_deliveries")
    op.drop_index(op.f("ix_github_deliveries_id"), table_name="github_deliveries")
    op.drop_table("github_deliveries")

    op.drop_index(op.f("ix_pull_requests_author"), table_name="pull_requests")
    op.drop_index(op.f("ix_pull_requests_pr_number"), table_name="pull_requests")
    op.drop_index(op.f("ix_pull_requests_repository_name"), table_name="pull_requests")
    op.drop_index(op.f("ix_pull_requests_repository_id"), table_name="pull_requests")
    op.drop_index(op.f("ix_pull_requests_id"), table_name="pull_requests")
    op.drop_table("pull_requests")
