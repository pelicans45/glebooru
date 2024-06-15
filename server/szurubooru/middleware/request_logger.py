"""

from szurubooru.rest import middleware

from szurubooru.log import logger
from szurubooru import db, rest

#logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


@middleware.pre_hook
def process_request(_ctx: rest.Context) -> None:
    db.reset_query_count()


@middleware.post_hook
def process_response(ctx: rest.Context) -> None:
    logging.info(
        "%s %s (user=%s, queries=%d)",
        ctx.method,
        ctx.url,
        ctx.user.name,
        db.get_query_count(),
    )
"""
