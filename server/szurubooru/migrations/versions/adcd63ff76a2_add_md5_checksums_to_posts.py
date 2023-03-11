"""
Add MD5 checksums to posts

Revision ID: adcd63ff76a2
Created at: 2021-01-05 17:08:21.741601
"""

import sqlalchemy as sa
from sqlalchemy.sql import text
from alembic import op
from datetime import datetime

revision = "adcd63ff76a2"
down_revision = "c867abb456b1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("post", sa.Column("checksum_md5", sa.Unicode(32)))

    op.execute()

    anonymous_user = {
        "creation_time": datetime.min,
        "last_login_time": None,
        "version": 1,
        "name": "anonymous",
        "password_hash": "7ndJT4kWr2SaAsrnyTrXIkwGivLT9G322FQeZPFXeHcArCwZrESV8iQgGlaMxs1R35Z227C6de87foAdwmLfgF06SaozYynb6DftTIOcbqjgV2hp4JRtfKsLnlkAhyiZ",
        "password_salt": "VweZx3J8c5MgMweyU82Ul1AjxmlzTbtP",
        "password_revision": 0,
        "email": "anon@anon.anon",
        "rank": "anonymous",
        "avatar_style": "gravatar",
    }
    conn = op.get_bind()

    conn.execute(text("""INSERT INTO "user" (creation_time, last_login_time, version, name, password_hash, password_salt, password_revision, email, rank, avatar_style) VALUES (:creation_time, :last_login_time, :version, :name, :password_hash, :password_salt, :password_revision, :email, :rank, :avatar_style)"""), **anonymous_user)


def downgrade():
    op.drop_column("post", "checksum_md5")
