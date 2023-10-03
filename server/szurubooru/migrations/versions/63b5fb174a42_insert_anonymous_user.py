"""
Insert anonymous user

Revision ID: 63b5fb174a42
Created at: 2023-03-12 17:08:21.741601
"""

from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

revision = "63b5fb174a42"
down_revision = "adcd63ff76a2"
branch_labels = None
depends_on = None


def upgrade():
    return
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

    conn.execute(
        text(
            """INSERT INTO "user" (creation_time, last_login_time, version, name, password_hash, password_salt, password_revision, email, rank, avatar_style) VALUES (:creation_time, :last_login_time, :version, :name, :password_hash, :password_salt, :password_revision, :email, :rank, :avatar_style)"""
        ),
        **anonymous_user,
    )


def downgrade():
    return
    conn = op.get_bind()
    conn.execute(text("""DELETE FROM "user" WHERE name = 'anonymous'"""))
