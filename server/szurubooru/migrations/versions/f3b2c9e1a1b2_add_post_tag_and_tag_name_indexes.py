"""
Add indexes to speed up tag lookups in post listings

Revision ID: f3b2c9e1a1b2
Revises: c9f0d3b1a2e7
Created at: 2026-01-20
"""

from alembic import op

revision = "f3b2c9e1a1b2"
down_revision = "c9f0d3b1a2e7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_post_tag_tag_id_post_id",
        "post_tag",
        ["tag_id", "post_id"],
        unique=False,
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_tag_name_lower_name "
        "ON tag_name (lower(name))"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_tag_name_lower_name")
    op.drop_index("ix_post_tag_tag_id_post_id", table_name="post_tag")
