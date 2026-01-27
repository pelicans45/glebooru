import contextlib
import os
import random
import string
import uuid
from datetime import datetime
from unittest.mock import patch

import freezegun
import pytest
import psycopg
import sqlalchemy as sa
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import orm
from sqlalchemy.pool import NullPool

from szurubooru import config, db, model, rest


def get_unique_name():
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(8))


@pytest.fixture
def fake_datetime():
    @contextlib.contextmanager
    def injector(now):
        freezer = freezegun.freeze_time(now)
        freezer.start()
        yield
        freezer.stop()

    return injector


@pytest.fixture(scope="session")
def query_logger(pytestconfig):
    if pytestconfig.option.verbose > 0:
        import logging

        import coloredlogs

        coloredlogs.install(
            fmt="[%(asctime)-15s] %(name)s %(message)s", isatty=True
        )
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def _get_env_setting(name, default):
    value = os.getenv(name)
    if value:
        return value
    return default


def _postgres_settings():
    return {
        "host": _get_env_setting("POSTGRES_HOST", "localhost"),
        "port": int(_get_env_setting("POSTGRES_PORT", "5432")),
        "user": _get_env_setting("POSTGRES_USER", "postgres"),
        "password": _get_env_setting("POSTGRES_PASSWORD", ""),
        "admin_db": _get_env_setting("POSTGRES_DB", "postgres"),
    }


def _sqlalchemy_url(**kwargs):
    return sa.engine.URL.create(
        "postgresql+psycopg",
        username=kwargs["user"],
        password=kwargs["password"] or None,
        host=kwargs["host"],
        port=kwargs["port"],
        database=kwargs["dbname"],
    )


def _load_database(**kwargs):
    engine = sa.create_engine(_sqlalchemy_url(**kwargs), poolclass=NullPool)
    with engine.begin() as connection:
        model.Base.metadata.create_all(connection)
    engine.dispose()


_PG_SETTINGS = _postgres_settings()
postgresql_noproc = factories.postgresql_noproc(
    host=_PG_SETTINGS["host"],
    port=_PG_SETTINGS["port"],
    user=_PG_SETTINGS["user"],
    password=_PG_SETTINGS["password"],
    dbname=_PG_SETTINGS["admin_db"],
)
_CREATED_DATABASES = set()


@pytest.fixture(scope="function")
def postgresql(postgresql_noproc):
    dbname = f"pytest_{uuid.uuid4().hex}"
    janitor = DatabaseJanitor(
        user=postgresql_noproc.user,
        host=postgresql_noproc.host,
        port=postgresql_noproc.port,
        dbname=dbname,
        template_dbname=postgresql_noproc.template_dbname,
        version=postgresql_noproc.version,
        password=postgresql_noproc.password,
    )
    with janitor:
        db_connection = psycopg.connect(
            dbname=dbname,
            user=postgresql_noproc.user,
            password=postgresql_noproc.password,
            host=postgresql_noproc.host,
            port=postgresql_noproc.port,
            options=postgresql_noproc.options,
        )
        yield db_connection
        db_connection.close()


def _create_session(postgresql_connection):
    info = postgresql_connection.info
    db_key = (info.host, info.port, info.user, info.dbname)
    if db_key not in _CREATED_DATABASES:
        _load_database(
            host=info.host or _PG_SETTINGS["host"],
            port=info.port or _PG_SETTINGS["port"],
            user=info.user or _PG_SETTINGS["user"],
            password=_PG_SETTINGS["password"],
            dbname=info.dbname,
        )
        _CREATED_DATABASES.add(db_key)
    engine = sa.create_engine(
        _sqlalchemy_url(
            user=info.user or _PG_SETTINGS["user"],
            password=_PG_SETTINGS["password"],
            host=info.host or _PG_SETTINGS["host"],
            port=info.port or _PG_SETTINGS["port"],
            dbname=info.dbname,
        ),
        poolclass=NullPool,
    )
    session_factory = orm.sessionmaker(bind=engine, autoflush=False)
    session = session_factory()
    _attach_statistics_refresher(session)
    return session, engine


# Tests use create_all() so stats triggers aren't installed; recompute stats.
def _refresh_statistics(connection: sa.Connection) -> None:
    connection.execute(sa.text("DELETE FROM database_statistics"))
    connection.execute(sa.text("DELETE FROM tag_category_statistics"))
    connection.execute(sa.text("DELETE FROM pool_category_statistics"))
    connection.execute(sa.text("DELETE FROM tag_statistics"))
    connection.execute(sa.text("DELETE FROM post_statistics"))
    connection.execute(sa.text("DELETE FROM pool_statistics"))
    connection.execute(sa.text("DELETE FROM user_statistics"))
    connection.execute(sa.text("DELETE FROM comment_statistics"))

    connection.execute(
        sa.text(
            """
            INSERT INTO database_statistics (
                id, post_count, tag_count, pool_count, user_count, comment_count
            )
            SELECT
                TRUE,
                (SELECT COUNT(*) FROM post),
                (SELECT COUNT(*) FROM tag),
                (SELECT COUNT(*) FROM pool),
                (SELECT COUNT(*) FROM "user"),
                (SELECT COUNT(*) FROM comment)
            """
        )
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO tag_category_statistics (category_id, usage_count)
            SELECT
                tc.id,
                COALESCE(COUNT(t.id), 0)
            FROM tag_category tc
            LEFT JOIN tag t ON t.category_id = tc.id
            GROUP BY tc.id
            """
        )
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO pool_category_statistics (category_id, usage_count)
            SELECT
                pc.id,
                COALESCE(COUNT(p.id), 0)
            FROM pool_category pc
            LEFT JOIN pool p ON p.category_id = pc.id
            GROUP BY pc.id
            """
        )
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO tag_statistics (
                tag_id, usage_count, suggestion_count, implication_count
            )
            SELECT
                t.id,
                COALESCE(pt.cnt, 0) AS usage_count,
                COALESCE(ts.cnt, 0) AS suggestion_count,
                COALESCE(ti.cnt, 0) AS implication_count
            FROM tag t
            LEFT JOIN (
                SELECT tag_id, COUNT(*) AS cnt
                FROM post_tag
                GROUP BY tag_id
            ) pt ON pt.tag_id = t.id
            LEFT JOIN (
                SELECT parent_id AS tag_id, COUNT(*) AS cnt
                FROM tag_suggestion
                GROUP BY parent_id
            ) ts ON ts.tag_id = t.id
            LEFT JOIN (
                SELECT parent_id AS tag_id, COUNT(*) AS cnt
                FROM tag_implication
                GROUP BY parent_id
            ) ti ON ti.tag_id = t.id
            """
        )
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO post_statistics (
                post_id, tag_count, pool_count, note_count, comment_count,
                relation_count, score, favorite_count, feature_count,
                last_comment_creation_time, last_comment_edit_time,
                last_favorite_time, last_feature_time
            )
            SELECT
                p.id,
                COALESCE(pt.cnt, 0) AS tag_count,
                COALESCE(pp.cnt, 0) AS pool_count,
                COALESCE(pn.cnt, 0) AS note_count,
                COALESCE(pc.cnt, 0) AS comment_count,
                COALESCE(pr.cnt, 0) AS relation_count,
                COALESCE(ps.sum_score, 0) AS score,
                COALESCE(pf.cnt, 0) AS favorite_count,
                COALESCE(pfeat.cnt, 0) AS feature_count,
                pc.max_creation,
                pc.max_edit,
                pf.max_time,
                pfeat.max_time
            FROM post p
            LEFT JOIN (
                SELECT post_id, COUNT(*) AS cnt
                FROM post_tag
                GROUP BY post_id
            ) pt ON pt.post_id = p.id
            LEFT JOIN (
                SELECT post_id, COUNT(*) AS cnt
                FROM pool_post
                GROUP BY post_id
            ) pp ON pp.post_id = p.id
            LEFT JOIN (
                SELECT post_id, COUNT(*) AS cnt
                FROM post_note
                GROUP BY post_id
            ) pn ON pn.post_id = p.id
            LEFT JOIN (
                SELECT
                    post_id,
                    COUNT(*) AS cnt,
                    MAX(creation_time) AS max_creation,
                    MAX(last_edit_time) AS max_edit
                FROM comment
                GROUP BY post_id
            ) pc ON pc.post_id = p.id
            LEFT JOIN (
                SELECT post_id, SUM(score) AS sum_score
                FROM post_score
                GROUP BY post_id
            ) ps ON ps.post_id = p.id
            LEFT JOIN (
                SELECT
                    post_id,
                    COUNT(*) AS cnt,
                    MAX(time) AS max_time
                FROM post_favorite
                GROUP BY post_id
            ) pf ON pf.post_id = p.id
            LEFT JOIN (
                SELECT
                    post_id,
                    COUNT(*) AS cnt,
                    MAX(time) AS max_time
                FROM post_feature
                GROUP BY post_id
            ) pfeat ON pfeat.post_id = p.id
            LEFT JOIN (
                SELECT post_id, COUNT(*) AS cnt
                FROM (
                    SELECT parent_id AS post_id FROM post_relation
                    UNION ALL
                    SELECT child_id AS post_id FROM post_relation
                ) rel
                GROUP BY post_id
            ) pr ON pr.post_id = p.id
            """
        )
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO pool_statistics (pool_id, post_count)
            SELECT
                p.id,
                COALESCE(pp.cnt, 0) AS post_count
            FROM pool p
            LEFT JOIN (
                SELECT pool_id, COUNT(*) AS cnt
                FROM pool_post
                GROUP BY pool_id
            ) pp ON pp.pool_id = p.id
            """
        )
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO user_statistics (user_id, upload_count, comment_count, favorite_count)
            SELECT
                u.id,
                COALESCE(p.cnt, 0) AS upload_count,
                COALESCE(c.cnt, 0) AS comment_count,
                COALESCE(f.cnt, 0) AS favorite_count
            FROM "user" u
            LEFT JOIN (
                SELECT user_id, COUNT(*) AS cnt
                FROM post
                WHERE user_id IS NOT NULL
                GROUP BY user_id
            ) p ON p.user_id = u.id
            LEFT JOIN (
                SELECT user_id, COUNT(*) AS cnt
                FROM comment
                WHERE user_id IS NOT NULL
                GROUP BY user_id
            ) c ON c.user_id = u.id
            LEFT JOIN (
                SELECT user_id, COUNT(*) AS cnt
                FROM post_favorite
                WHERE user_id IS NOT NULL
                GROUP BY user_id
            ) f ON f.user_id = u.id
            """
        )
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO comment_statistics (comment_id, score)
            SELECT
                c.id,
                COALESCE(cs.sum_score, 0) AS score
            FROM comment c
            LEFT JOIN (
                SELECT comment_id, SUM(score) AS sum_score
                FROM comment_score
                GROUP BY comment_id
            ) cs ON cs.comment_id = c.id
            """
        )
    )


def _attach_statistics_refresher(session: orm.Session) -> None:
    def _after_flush_postexec(_session, _flush_context) -> None:
        if _session.info.get("_refreshing_statistics"):
            return
        _session.info["_refreshing_statistics"] = True
        try:
            _refresh_statistics(_session.connection())
        finally:
            _session.info["_refreshing_statistics"] = False

    sa.event.listen(session, "after_flush_postexec", _after_flush_postexec)


@pytest.fixture(scope="function")
def postgres_session(postgresql):
    session, engine = _create_session(postgresql)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


@pytest.fixture(scope="function")
def postgres_session_nontransacted(postgresql):
    session, engine = _create_session(postgresql)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def session(query_logger, postgres_session):
    db.session = postgres_session
    try:
        yield postgres_session
    finally:
        postgres_session.rollback()
        postgres_session.close()


@pytest.fixture(scope="function")
def nontransacted_session(query_logger, postgres_session_nontransacted):
    old_db_session = db.session
    db.session = postgres_session_nontransacted
    try:
        yield postgres_session_nontransacted
    finally:
        postgres_session_nontransacted.rollback()
        postgres_session_nontransacted.close()
        db.session = old_db_session


@pytest.fixture
def context_factory(session):
    def factory(params=None, files=None, user=None, headers=None):
        ctx = rest.Context(
            env={"HTTP_ORIGIN": "http://example.com"},
            method=None,
            url=None,
            headers=headers or {},
            params=params or {},
            files=files or {},
        )
        ctx.session = session
        ctx.user = user or model.User()
        return ctx

    return factory


@pytest.fixture
def config_injector():
    def injector(new_config_content):
        config.config = new_config_content

    return injector


@pytest.fixture
def user_factory():
    def factory(
        name=None,
        rank=model.User.RANK_REGULAR,
        email="dummy",
        password_salt=None,
        password_hash=None,
    ):
        user = model.User()
        user.name = name or get_unique_name()
        user.password_salt = password_salt or "dummy"
        user.password_hash = password_hash or "dummy"
        user.email = email
        user.rank = rank
        user.creation_time = datetime(1997, 1, 1)
        user.avatar_style = model.User.AVATAR_GRAVATAR
        return user

    return factory


@pytest.fixture
def user_token_factory(user_factory):
    def factory(
        user=None,
        token=None,
        expiration_time=None,
        enabled=None,
        creation_time=None,
    ):
        if user is None:
            user = user_factory()
            db.session.add(user)
        user_token = model.UserToken()
        user_token.user = user
        user_token.token = token or "dummy"
        user_token.expiration_time = expiration_time
        user_token.enabled = enabled if enabled is not None else True
        user_token.creation_time = creation_time or datetime(1997, 1, 1)
        return user_token

    return factory


@pytest.fixture
def tag_category_factory():
    def factory(name=None, color="dummy", order=1, default=False):
        category = model.TagCategory()
        category.name = name or get_unique_name()
        category.color = color
        category.order = order
        category.default = default
        return category

    return factory


@pytest.fixture
def tag_factory():
    def factory(names=None, category=None):
        if not category:
            category = model.TagCategory(get_unique_name())
            db.session.add(category)
        tag = model.Tag()
        tag.names = []
        for i, name in enumerate(names or [get_unique_name()]):
            tag.names.append(model.TagName(name, i))
        tag.category = category
        tag.creation_time = datetime(1996, 1, 1)
        return tag

    return factory


@pytest.fixture
def post_factory():
    def factory(
        id=None,
        safety=model.Post.SAFETY_SAFE,
        type=model.Post.TYPE_IMAGE,
        checksum=None,
        tags=None,
    ):
        post = model.Post()
        post.post_id = id
        post.safety = safety
        post.type = type
        post.checksum = checksum or get_unique_name()
        post.flags = []
        post.mime_type = "application/octet-stream"
        post.creation_time = datetime(1996, 1, 1)
        post.tags = list(tags) if tags else []
        return post

    return factory


@pytest.fixture
def comment_factory(user_factory, post_factory):
    def factory(user=None, post=None, text="dummy", time=None):
        if not user:
            user = user_factory()
            db.session.add(user)
        if not post:
            post = post_factory()
            db.session.add(post)
        comment = model.Comment()
        comment.user = user
        comment.post = post
        comment.text = text
        comment.creation_time = time or datetime(1996, 1, 1)
        return comment

    return factory


@pytest.fixture
def post_score_factory(user_factory, post_factory):
    def factory(post=None, user=None, score=1):
        if user is None:
            user = user_factory()
        if post is None:
            post = post_factory()
        return model.PostScore(
            post=post, user=user, score=score, time=datetime(1999, 1, 1)
        )

    return factory


@pytest.fixture
def post_favorite_factory(user_factory, post_factory):
    def factory(post=None, user=None):
        if user is None:
            user = user_factory()
        if post is None:
            post = post_factory()
        return model.PostFavorite(
            post=post, user=user, time=datetime(1999, 1, 1)
        )

    return factory


@pytest.fixture
def pool_category_factory():
    def factory(name=None, color="dummy", default=False):
        category = model.PoolCategory()
        category.name = name or get_unique_name()
        category.color = color
        category.default = default
        return category

    return factory


@pytest.fixture
def pool_factory():
    def factory(
        id=None, names=None, description=None, category=None, time=None
    ):
        if not category:
            category = model.PoolCategory(get_unique_name())
            db.session.add(category)
        pool = model.Pool()
        pool.pool_id = id
        pool.names = []
        for i, name in enumerate(names or [get_unique_name()]):
            pool.names.append(model.PoolName(name, i))
        pool.description = description
        pool.category = category
        pool.creation_time = time or datetime(1996, 1, 1)
        return pool

    return factory


@pytest.fixture
def pool_post_factory(pool_factory, post_factory):
    def factory(pool=None, post=None, order=None):
        if not pool:
            pool = pool_factory()
            db.session.add(pool)
        if not post:
            post = post_factory()
            db.session.add(post)
        pool_post = model.PoolPost(post)
        pool_post.pool = pool
        pool_post.post = post
        pool_post.order = order or 0
        return pool_post

    return factory


@pytest.fixture
def read_asset():
    def get(path):
        path = os.path.join(os.path.dirname(__file__), "assets", path)
        with open(path, "rb") as handle:
            return handle.read()

    return get
