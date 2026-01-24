import sqlalchemy as sa

from szurubooru.model.base import Base


class TagSuggestion(Base):
    __tablename__ = "tag_suggestion"

    parent_id = sa.Column(
        "parent_id",
        sa.Integer,
        sa.ForeignKey("tag.id"),
        nullable=False,
        primary_key=True,
        index=True,
    )
    child_id = sa.Column(
        "child_id",
        sa.Integer,
        sa.ForeignKey("tag.id"),
        nullable=False,
        primary_key=True,
        index=True,
    )

    def __init__(self, parent_id: int, child_id: int) -> None:
        self.parent_id = parent_id
        self.child_id = child_id


class TagImplication(Base):
    __tablename__ = "tag_implication"

    parent_id = sa.Column(
        "parent_id",
        sa.Integer,
        sa.ForeignKey("tag.id"),
        nullable=False,
        primary_key=True,
        index=True,
    )
    child_id = sa.Column(
        "child_id",
        sa.Integer,
        sa.ForeignKey("tag.id"),
        nullable=False,
        primary_key=True,
        index=True,
    )

    def __init__(self, parent_id: int, child_id: int) -> None:
        self.parent_id = parent_id
        self.child_id = child_id


class TagName(Base):
    __tablename__ = "tag_name"

    tag_name_id = sa.Column("tag_name_id", sa.Integer, primary_key=True)
    tag_id = sa.Column(
        "tag_id",
        sa.Integer,
        sa.ForeignKey("tag.id"),
        nullable=False,
        index=True,
    )
    name = sa.Column("name", sa.Unicode(128), nullable=False, unique=True)
    order = sa.Column("ord", sa.Integer, nullable=False, index=True)

    def __init__(self, name: str, order: int) -> None:
        self.name = name
        self.order = order


class Tag(Base):
    __tablename__ = "tag"

    tag_id = sa.Column("id", sa.Integer, primary_key=True)
    category_id = sa.Column(
        "category_id",
        sa.Integer,
        sa.ForeignKey("tag_category.id"),
        nullable=False,
        index=True,
    )
    version = sa.Column("version", sa.Integer, default=1, nullable=False)
    creation_time = sa.Column("creation_time", sa.DateTime, nullable=False)
    last_edit_time = sa.Column("last_edit_time", sa.DateTime)
    description = sa.Column("description", sa.UnicodeText, default=None)

    category = sa.orm.relationship("TagCategory", lazy="joined")
    names = sa.orm.relationship(
        "TagName",
        cascade="all,delete-orphan",
        lazy="joined",
        order_by="TagName.order",
    )
    statistics = sa.orm.relationship(
        "TagStatistics",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="joined",
        backref=sa.orm.backref("tag", lazy="joined"),
    )
    suggestions = sa.orm.relationship(
        "Tag",
        secondary="tag_suggestion",
        primaryjoin=tag_id == TagSuggestion.parent_id,
        secondaryjoin=tag_id == TagSuggestion.child_id,
        lazy="joined",
    )
    implications = sa.orm.relationship(
        "Tag",
        secondary="tag_implication",
        primaryjoin=tag_id == TagImplication.parent_id,
        secondaryjoin=tag_id == TagImplication.child_id,
        lazy="joined",
    )
    first_name = sa.orm.column_property(
        (
            sa.sql.expression.select(TagName.name)
            .where(TagName.tag_id == tag_id)
            .order_by(TagName.order)
            .limit(1)
            .scalar_subquery()
        ),
        deferred=True,
    )

    @property
    def post_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.usage_count or 0)

    @property
    def suggestion_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.suggestion_count or 0)

    @property
    def implication_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.implication_count or 0)

    __mapper_args__ = {
        "version_id_col": version,
        "version_id_generator": False,
    }
