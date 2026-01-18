"""
Add duration to posts

Revision ID: c9f0d3b1a2e7
Created at: 2025-02-14 00:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "c9f0d3b1a2e7"
down_revision = "b6d3e94cf0b1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("post", sa.Column("duration", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("post", "duration")
