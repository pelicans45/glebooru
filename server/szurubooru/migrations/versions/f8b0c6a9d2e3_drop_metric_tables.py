'''
Drop metric tables

Revision ID: f8b0c6a9d2e3
Revises: 5b5c940b4e78, 0061c5c3299f
Created at: 2026-01-23 00:05:00.000000
'''

import sqlalchemy as sa
from alembic import op


revision = 'f8b0c6a9d2e3'
down_revision = ('5b5c940b4e78', '0061c5c3299f')
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(name)


def upgrade():
    if _has_table('post_metric_range'):
        op.drop_table('post_metric_range')
    if _has_table('post_metric'):
        op.drop_table('post_metric')
    if _has_table('metric'):
        op.drop_table('metric')


def _add_version_column(table: str) -> None:
    op.add_column(table, sa.Column('version', sa.Integer(), nullable=True))
    op.execute(
        sa.table(table, sa.column('version'))
        .update()
        .values(version=1)
    )
    op.alter_column(table, 'version', nullable=False)


def downgrade():
    op.create_table(
        'metric',
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('min', sa.Float(), nullable=False),
        sa.Column('max', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('tag_id'),
    )
    op.create_table(
        'post_metric',
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('post_id', 'tag_id'),
    )
    op.create_table(
        'post_metric_range',
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('post_id', 'tag_id'),
    )
    op.create_foreign_key(
        None, 'metric', 'tag', ['tag_id'], ['id']
    )
    op.create_foreign_key(
        None, 'post_metric', 'post', ['post_id'], ['id']
    )
    op.create_foreign_key(
        None, 'post_metric', 'metric', ['tag_id'], ['tag_id']
    )
    op.create_foreign_key(
        None, 'post_metric_range', 'post', ['post_id'], ['id']
    )
    op.create_foreign_key(
        None, 'post_metric_range', 'metric', ['tag_id'], ['tag_id']
    )
    _add_version_column('metric')
    _add_version_column('post_metric')
    _add_version_column('post_metric_range')
    op.create_foreign_key(
        'post_metric_post_tag_fkey', 'post_metric', 'post_tag',
        ['post_id', 'tag_id'], ['post_id', 'tag_id'],
        ondelete='cascade')
    op.create_foreign_key(
        'post_metric_range_post_tag_fkey', 'post_metric_range', 'post_tag',
        ['post_id', 'tag_id'], ['post_id', 'tag_id'],
        ondelete='cascade')
