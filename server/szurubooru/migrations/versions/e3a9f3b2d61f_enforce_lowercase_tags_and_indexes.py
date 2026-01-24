"""
Enforce lowercase tag names and add tag lookup indexes.

Revision ID: e3a9f3b2d61f
Revises: d2b4f8c19a7c
Created at: 2026-01-23
"""

from alembic import op


revision = "e3a9f3b2d61f"
down_revision = "d2b4f8c19a7c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE tag_name SET name = lower(name)")
    op.execute(
        "ALTER TABLE tag_name "
        "ADD CONSTRAINT ck_tag_name_lowercase "
        "CHECK (name = lower(name))"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_post_tag_tag_id_post_id "
        "ON post_tag (tag_id, post_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_tag_name_name_pattern "
        "ON tag_name (name text_pattern_ops)"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_tag_name_name_pattern")
    op.execute("DROP INDEX IF EXISTS ix_post_tag_tag_id_post_id")
    op.execute(
        "ALTER TABLE tag_name "
        "DROP CONSTRAINT IF EXISTS ck_tag_name_lowercase"
    )
