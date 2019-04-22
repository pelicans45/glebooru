'''
PostMetric depends on PostTag

Revision ID: 0061c5c3299f
Created at: 2019-04-20 14:02:23.229492
'''

import sqlalchemy as sa
from alembic import op


revision = '0061c5c3299f'
down_revision = 'aae2050fb28c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        'post_metric_post_tag_fkey', 'post_metric', 'post_tag',
        ['post_id', 'tag_id'], ['post_id', 'tag_id'],
        ondelete='cascade')
    op.create_foreign_key(
        'post_metric_range_post_tag_fkey', 'post_metric_range', 'post_tag',
        ['post_id', 'tag_id'], ['post_id', 'tag_id'],
        ondelete='cascade')


def downgrade():
    op.drop_constraint(
        'post_metric_post_tag_fkey', 'post_metric',
        type_='foreignKey')
    op.drop_constraint(
        'post_metric_range_post_tag_fkey', 'post_metric',
        type_='foreignKey')
