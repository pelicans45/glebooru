import logging

from szurubooru.rest import middleware

from szurubooru import db, rest

logger = logging.getLogger(__name__)
#logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


@middleware.pre_hook
def process_request(_ctx: rest.Context) -> None:
    db.reset_query_count()


@middleware.post_hook
def process_response(ctx: rest.Context) -> None:
    logger.info(
        "%s %s (user=%s, queries=%d)",
        ctx.method,
        ctx.url,
        ctx.user.name,
        db.get_query_count(),
    )
