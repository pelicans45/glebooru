from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from szurubooru.model.base import Base
from szurubooru.model.comment import Comment
from szurubooru.model.pool import PoolPost


class PostFeature(Base):
    __tablename__ = "post_feature"

    post_feature_id = sa.Column("id", sa.Integer, primary_key=True)
    post_id = sa.Column(
        "post_id",
        sa.Integer,
        sa.ForeignKey("post.id"),
        nullable=False,
        index=True,
    )
    user_id = sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    time = sa.Column("time", sa.DateTime, nullable=False)

    post = sa.orm.relationship("Post", back_populates="features")  # type: Post
    user = sa.orm.relationship(
        "User",
        backref=sa.orm.backref("post_features", cascade="all, delete-orphan"),
    )


class PostScore(Base):
    __tablename__ = "post_score"
    __mapper_args__ = {"confirm_deleted_rows": False}

    post_id = sa.Column(
        "post_id",
        sa.Integer,
        sa.ForeignKey("post.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    user_id = sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("user.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    time = sa.Column("time", sa.DateTime, nullable=False)
    score = sa.Column("score", sa.Integer, nullable=False)

    post = sa.orm.relationship("Post")
    user = sa.orm.relationship(
        "User",
        backref=sa.orm.backref("post_scores", cascade="all, delete-orphan"),
    )


class PostFavorite(Base):
    __tablename__ = "post_favorite"
    __mapper_args__ = {"confirm_deleted_rows": False}

    post_id = sa.Column(
        "post_id",
        sa.Integer,
        sa.ForeignKey("post.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    user_id = sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("user.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    time = sa.Column("time", sa.DateTime, nullable=False)

    post = sa.orm.relationship("Post")
    user = sa.orm.relationship(
        "User",
        lazy="joined",
        backref=sa.orm.backref("post_favorites", cascade="all, delete-orphan"),
    )


class PostNote(Base):
    __tablename__ = "post_note"

    post_note_id = sa.Column("id", sa.Integer, primary_key=True)
    post_id = sa.Column(
        "post_id",
        sa.Integer,
        sa.ForeignKey("post.id"),
        nullable=False,
        index=True,
    )
    polygon = sa.Column("polygon", sa.PickleType, nullable=False)
    text = sa.Column("text", sa.UnicodeText, nullable=False)

    post = sa.orm.relationship("Post")


class PostRelation(Base):
    __tablename__ = "post_relation"

    parent_id = sa.Column(
        "parent_id",
        sa.Integer,
        sa.ForeignKey("post.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    child_id = sa.Column(
        "child_id",
        sa.Integer,
        sa.ForeignKey("post.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    def __init__(self, parent_id: int, child_id: int) -> None:
        self.parent_id = parent_id
        self.child_id = child_id


class PostTag(Base):
    __tablename__ = "post_tag"

    post_id = sa.Column(
        "post_id",
        sa.Integer,
        sa.ForeignKey("post.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    tag_id = sa.Column(
        "tag_id",
        sa.Integer,
        sa.ForeignKey("tag.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    def __init__(self, post_id: int, tag_id: int) -> None:
        self.post_id = post_id
        self.tag_id = tag_id


class PostSignature(Base):
    __tablename__ = "post_signature"
    __mapper_args__ = {"confirm_deleted_rows": False}

    post_id = sa.Column(
        "post_id",
        sa.Integer,
        sa.ForeignKey("post.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    signature = sa.Column("signature", sa.LargeBinary, nullable=False)
    words = sa.Column(
        "words",
        sa.dialects.postgresql.ARRAY(sa.Integer, dimensions=1),
        nullable=False,
        index=True,
    )

    post = sa.orm.relationship("Post")


class Post(Base):
    __tablename__ = "post"

    SAFETY_SAFE = "safe"
    SAFETY_SKETCHY = "sketchy"
    SAFETY_UNSAFE = "unsafe"

    TYPE_IMAGE = "image"
    TYPE_ANIMATION = "animation"
    TYPE_VIDEO = "video"
    TYPE_AUDIO = "audio"
    TYPE_FLASH = "flash"

    FLAG_LOOP = "loop"
    FLAG_SOUND = "sound"

    # basic meta
    post_id = sa.Column("id", sa.Integer, primary_key=True)
    user_id = sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    version = sa.Column("version", sa.Integer, default=1, nullable=False)
    creation_time = sa.Column("creation_time", sa.DateTime, nullable=False)
    last_edit_time = sa.Column("last_edit_time", sa.DateTime)
    safety = sa.Column("safety", sa.Unicode(32), nullable=False)
    source = sa.Column("source", sa.Unicode(2048))
    flags_string = sa.Column("flags", sa.Unicode(32), default="")

    # content description
    type = sa.Column("type", sa.Unicode(32), nullable=False)
    checksum = sa.Column(
        "checksum", sa.Unicode(64), nullable=False, index=True, unique=True
    )
    checksum_md5 = sa.Column("checksum_md5", sa.Unicode(32))
    file_size = sa.Column("file_size", sa.BigInteger)
    canvas_width = sa.Column("image_width", sa.Integer)
    canvas_height = sa.Column("image_height", sa.Integer)
    mime_type = sa.Column("mime-type", sa.Unicode(32), nullable=False)
    duration = sa.Column("duration", sa.Integer)

    # foreign tables
    user = sa.orm.relationship("User")
    tags = sa.orm.relationship("Tag", backref="posts", secondary="post_tag")
    signature = sa.orm.relationship(
        "PostSignature",
        uselist=False,
        cascade="all, delete, delete-orphan",
        lazy="select",
        overlaps="post",
    )
    relations = sa.orm.relationship(
        "Post",
        secondary="post_relation",
        primaryjoin=post_id == PostRelation.parent_id,
        secondaryjoin=post_id == PostRelation.child_id,
        lazy="select",
        backref="related_by",
    )
    features = sa.orm.relationship(
        "PostFeature",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="select",
    )
    scores = sa.orm.relationship(
        "PostScore", cascade="all, delete-orphan", lazy="select", overlaps="post"
    )
    favorited_by = sa.orm.relationship(
        "PostFavorite", cascade="all, delete-orphan", lazy="select", overlaps="post"
    )
    notes = sa.orm.relationship(
        "PostNote", cascade="all, delete-orphan", lazy="select", overlaps="post"
    )
    comments = sa.orm.relationship(
        "Comment", cascade="all, delete-orphan", overlaps="post"
    )
    _pools = sa.orm.relationship(
        "PoolPost",
        cascade="all,delete-orphan",
        lazy="select",
        order_by="PoolPost.order",
        back_populates="post",
    )
    pools = association_proxy("_pools", "pool")
    statistics = sa.orm.relationship(
        "PostStatistics",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="select",
        backref=sa.orm.backref("post", lazy="joined"),
    )

    canvas_area = sa.orm.column_property(canvas_width * canvas_height)
    canvas_aspect_ratio = sa.orm.column_property(
        sa.sql.expression.func.cast(canvas_width, sa.Float)
        / sa.sql.expression.func.cast(canvas_height, sa.Float)
    )

    @property
    def is_featured(self) -> bool:
        featured_post = (
            sa.orm.object_session(self)
            .query(PostFeature)
            .order_by(PostFeature.time.desc())
            .first()
        )
        return featured_post and featured_post.post_id == self.post_id

    @hybrid_property
    def flags(self) -> List[str]:
        return sorted(x for x in self.flags_string.split(",") if x)

    @flags.setter
    def flags(self, data: List[str]) -> None:
        self.flags_string = ",".join(x for x in data if x)

    @property
    def tag_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.tag_count or 0)

    @property
    def score(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.score or 0)

    @property
    def favorite_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.favorite_count or 0)

    @property
    def last_favorite_time(self):
        return self.statistics.last_favorite_time if self.statistics else None

    @property
    def feature_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.feature_count or 0)

    @property
    def last_feature_time(self):
        return self.statistics.last_feature_time if self.statistics else None

    @property
    def comment_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.comment_count or 0)

    @property
    def last_comment_creation_time(self):
        return self.statistics.last_comment_creation_time if self.statistics else None

    @property
    def last_comment_edit_time(self):
        return self.statistics.last_comment_edit_time if self.statistics else None

    @property
    def note_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.note_count or 0)

    @property
    def relation_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.relation_count or 0)

    __mapper_args__ = {
        "version_id_col": version,
        "version_id_generator": False,
    }
