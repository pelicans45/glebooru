'''
Add version to metric tables

Revision ID: aae2050fb28c
Created at: 2019-04-16 22:15:03.656192
'''

import sqlalchemy as sa
from alembic import op


revision = 'aae2050fb28c'
down_revision = '51ac43760440'
branch_labels = None
depends_on = None

tables = ['metric', 'post_metric', 'post_metric_range']


def upgrade():
    for table in tables:
        op.add_column(table, sa.Column('version', sa.Integer(), nullable=True))
        op.execute(
            sa.table(table, sa.column('version'))
            .update()
            .values(version=1))
        op.alter_column(table, 'version', nullable=False)


def downgrade():
    for table in tables:
        op.drop_column(table, 'version')
