import sqlalchemy as sa

from szurubooru.model.base import Base


class DatabaseStatistics(Base):
    __tablename__ = "database_statistics"

    id = sa.Column(
        "id",
        sa.Boolean,
        primary_key=True,
        nullable=False,
        server_default=sa.text("true"),
    )
    post_count = sa.Column(
        "post_count", sa.BigInteger, nullable=False, server_default="0"
    )
    tag_count = sa.Column(
        "tag_count", sa.BigInteger, nullable=False, server_default="0"
    )
    pool_count = sa.Column(
        "pool_count", sa.BigInteger, nullable=False, server_default="0"
    )
    user_count = sa.Column(
        "user_count", sa.BigInteger, nullable=False, server_default="0"
    )
    comment_count = sa.Column(
        "comment_count", sa.BigInteger, nullable=False, server_default="0"
    )


class TagStatistics(Base):
    __tablename__ = "tag_statistics"

    tag_id = sa.Column(
        "tag_id",
        sa.Integer,
        sa.ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    usage_count = sa.Column(
        "usage_count", sa.BigInteger, nullable=False, server_default="0"
    )
    suggestion_count = sa.Column(
        "suggestion_count", sa.BigInteger, nullable=False, server_default="0"
    )
    implication_count = sa.Column(
        "implication_count", sa.BigInteger, nullable=False, server_default="0"
    )


class PostStatistics(Base):
    __tablename__ = "post_statistics"

    post_id = sa.Column(
        "post_id",
        sa.Integer,
        sa.ForeignKey("post.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    tag_count = sa.Column(
        "tag_count", sa.BigInteger, nullable=False, server_default="0"
    )
    pool_count = sa.Column(
        "pool_count", sa.BigInteger, nullable=False, server_default="0"
    )
    note_count = sa.Column(
        "note_count", sa.BigInteger, nullable=False, server_default="0"
    )
    comment_count = sa.Column(
        "comment_count", sa.BigInteger, nullable=False, server_default="0"
    )
    relation_count = sa.Column(
        "relation_count", sa.BigInteger, nullable=False, server_default="0"
    )
    score = sa.Column(
        "score", sa.BigInteger, nullable=False, server_default="0"
    )
    favorite_count = sa.Column(
        "favorite_count", sa.BigInteger, nullable=False, server_default="0"
    )
    feature_count = sa.Column(
        "feature_count", sa.BigInteger, nullable=False, server_default="0"
    )
    last_comment_creation_time = sa.Column(
        "last_comment_creation_time", sa.DateTime
    )
    last_comment_edit_time = sa.Column(
        "last_comment_edit_time", sa.DateTime
    )
    last_favorite_time = sa.Column("last_favorite_time", sa.DateTime)
    last_feature_time = sa.Column("last_feature_time", sa.DateTime)


class PoolStatistics(Base):
    __tablename__ = "pool_statistics"

    pool_id = sa.Column(
        "pool_id",
        sa.Integer,
        sa.ForeignKey("pool.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    post_count = sa.Column(
        "post_count", sa.BigInteger, nullable=False, server_default="0"
    )


class UserStatistics(Base):
    __tablename__ = "user_statistics"

    user_id = sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    upload_count = sa.Column(
        "upload_count", sa.BigInteger, nullable=False, server_default="0"
    )
    comment_count = sa.Column(
        "comment_count", sa.BigInteger, nullable=False, server_default="0"
    )
    favorite_count = sa.Column(
        "favorite_count", sa.BigInteger, nullable=False, server_default="0"
    )


class CommentStatistics(Base):
    __tablename__ = "comment_statistics"

    comment_id = sa.Column(
        "comment_id",
        sa.Integer,
        sa.ForeignKey("comment.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    score = sa.Column(
        "score", sa.BigInteger, nullable=False, server_default="0"
    )


class TagCategoryStatistics(Base):
    __tablename__ = "tag_category_statistics"

    category_id = sa.Column(
        "category_id",
        sa.Integer,
        sa.ForeignKey("tag_category.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    usage_count = sa.Column(
        "usage_count", sa.BigInteger, nullable=False, server_default="0"
    )


class PoolCategoryStatistics(Base):
    __tablename__ = "pool_category_statistics"

    category_id = sa.Column(
        "category_id",
        sa.Integer,
        sa.ForeignKey("pool_category.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    usage_count = sa.Column(
        "usage_count", sa.BigInteger, nullable=False, server_default="0"
    )
