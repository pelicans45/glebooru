from typing import Optional

import sqlalchemy as sa

from szurubooru.model.base import Base


class PoolCategory(Base):
    __tablename__ = "pool_category"

    pool_category_id = sa.Column("id", sa.Integer, primary_key=True)
    version = sa.Column("version", sa.Integer, default=1, nullable=False)
    name = sa.Column("name", sa.Unicode(32), nullable=False)
    color = sa.Column(
        "color", sa.Unicode(32), nullable=False, default="#000000"
    )
    default = sa.Column("default", sa.Boolean, nullable=False, default=False)

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name
    statistics = sa.orm.relationship(
        "PoolCategoryStatistics",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="joined",
        backref=sa.orm.backref("category", lazy="joined"),
    )

    @property
    def pool_count(self) -> int:
        if not self.statistics:
            return 0
        return int(self.statistics.usage_count or 0)

    __mapper_args__ = {
        "version_id_col": version,
        "version_id_generator": False,
    }
