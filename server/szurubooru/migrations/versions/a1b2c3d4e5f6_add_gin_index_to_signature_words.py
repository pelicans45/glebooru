"""
Add GIN index to post_signature.words for faster reverse search

The reverse search uses word matching to find candidate similar images.
A GIN index on the words array column significantly speeds up queries
on large datasets by enabling efficient array containment checks.

Revision ID: a1b2c3d4e5f6
Revises: f3b2c9e1a1b2
Created at: 2026-01-22
"""

from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "f3b2c9e1a1b2"
branch_labels = None
depends_on = None


def upgrade():
    # Create GIN index on the words array column for faster lookups
    # This helps the reverse image search which matches words between signatures
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_post_signature_words_gin "
        "ON post_signature USING GIN (words)"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_post_signature_words_gin")
