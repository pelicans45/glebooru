"""
Add trigram index to tag names for fast wildcard search.

Revision ID: a4f1c2d3e4f5
Revises: e3a9f3b2d61f
Created at: 2026-01-23
"""

from alembic import op

revision = "a4f1c2d3e4f5"
down_revision = "e3a9f3b2d61f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX IF NOT EXISTS tag_name_name_trgm_idx "
        "ON tag_name USING gin (name gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS tag_name_name_trgm_idx")
