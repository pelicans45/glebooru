'''
Create metric tables

Revision ID: 51ac43760440
Created at: 2019-04-16 17:38:47.176916
'''

import sqlalchemy as sa
from alembic import op


revision = '51ac43760440'
down_revision = '1cd4c7b22846'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'metric',
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('min', sa.Float(), nullable=False),
        sa.Column('max', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['tag_id'], ['tag.id']),
        sa.PrimaryKeyConstraint('tag_id'))

    op.create_table(
        'post_metric',
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['post.id']),
        sa.ForeignKeyConstraint(['tag_id'], ['metric.tag_id']),
        sa.PrimaryKeyConstraint('post_id', 'tag_id'))

    op.create_table(
        'post_metric_range',
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['post.id']),
        sa.ForeignKeyConstraint(['tag_id'], ['metric.tag_id']),
        sa.PrimaryKeyConstraint('post_id', 'tag_id'))


def downgrade():
    op.drop_table('post_metric_range')
    op.drop_table('post_metric')
    op.drop_table('metric')
