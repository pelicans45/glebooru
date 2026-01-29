from datetime import datetime, UTC
from typing import Any, Callable, Optional, Tuple

from sqlalchemy.dialects.postgresql import insert as pg_insert

from szurubooru import db, errors, model


class InvalidFavoriteTargetError(errors.ValidationError):
    pass


def _get_table_info(
    entity: model.Base,
) -> Tuple[model.Base, Callable[[model.Base], Any]]:
    # assert entity
    resource_type, _, _ = model.util.get_resource_info(entity)
    if resource_type == "post":
        return model.PostFavorite, lambda table: table.post_id
    raise InvalidFavoriteTargetError()


def _get_fav_entity(entity: model.Base, user: model.User) -> model.Base:
    # assert entity
    # assert user
    return model.util.get_aux_entity(db.session, _get_table_info, entity, user)


def has_favorited(entity: model.Base, user: model.User) -> bool:
    # assert entity
    # assert user
    return _get_fav_entity(entity, user) is not None


def unset_favorite(entity: model.Base, user: Optional[model.User]) -> None:
    # assert entity
    # assert user
    fav_entity = _get_fav_entity(entity, user)
    if fav_entity:
        db.session.delete(fav_entity)


def set_favorite(entity: model.Base, user: Optional[model.User]) -> None:
    from szurubooru.func import scores

    # assert entity
    # assert user
    try:
        scores.set_score(entity, user, 1)
    except scores.InvalidScoreTargetError:
        pass
    table_cls, get_column = _get_table_info(entity)
    column_name = get_column(table_cls).name
    insert_stmt = pg_insert(table_cls.__table__).values(
        {
            column_name: get_column(entity),
            "user_id": user.user_id,
            "time": datetime.now(UTC).replace(tzinfo=None),
        }
    )
    insert_stmt = insert_stmt.on_conflict_do_nothing(
        index_elements=[column_name, "user_id"]
    )
    db.session.execute(insert_stmt)
