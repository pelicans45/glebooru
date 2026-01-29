import datetime
from typing import Any, Callable, Tuple

import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import insert as pg_insert

from szurubooru import db, errors, model


class InvalidScoreTargetError(errors.ValidationError):
    pass


class InvalidScoreValueError(errors.ValidationError):
    pass


def _ensure_user_id(user: model.User) -> None:
    if user is None:
        raise errors.AuthError("Authentication required")
    if user.user_id is None:
        db.session.add(user)
        db.session.flush()


def _refresh_score_statistics(entity: model.Base) -> None:
    resource_type, _, _ = model.util.get_resource_info(entity)
    if resource_type == "post":
        post_id = entity.post_id
        sum_score = db.session.execute(
            sa.select(sa.func.coalesce(sa.func.sum(model.PostScore.score), 0)).where(
                model.PostScore.post_id == post_id
            )
        ).scalar_one()
        insert_stmt = pg_insert(model.PostStatistics.__table__).values(
            {"post_id": post_id, "score": sum_score}
        )
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["post_id"], set_={"score": sum_score}
        )
        db.session.execute(insert_stmt)
        return
    if resource_type == "comment":
        comment_id = entity.comment_id
        sum_score = db.session.execute(
            sa.select(
                sa.func.coalesce(sa.func.sum(model.CommentScore.score), 0)
            ).where(model.CommentScore.comment_id == comment_id)
        ).scalar_one()
        insert_stmt = pg_insert(model.CommentStatistics.__table__).values(
            {"comment_id": comment_id, "score": sum_score}
        )
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["comment_id"], set_={"score": sum_score}
        )
        db.session.execute(insert_stmt)


def _get_table_info(
    entity: model.Base,
) -> Tuple[model.Base, Callable[[model.Base], Any]]:
    # assert entity
    resource_type, _, _ = model.util.get_resource_info(entity)
    if resource_type == "post":
        return model.PostScore, lambda table: table.post_id
    elif resource_type == "comment":
        return model.CommentScore, lambda table: table.comment_id
    raise InvalidScoreTargetError()


def _get_score_entity(entity: model.Base, user: model.User) -> model.Base:
    # assert user
    return model.util.get_aux_entity(db.session, _get_table_info, entity, user)


def delete_score(entity: model.Base, user: model.User) -> None:
    # assert entity
    # assert user
    _ensure_user_id(user)
    score_entity = _get_score_entity(entity, user)
    if score_entity:
        db.session.delete(score_entity)
        _refresh_score_statistics(entity)
        db.session.expire(entity, ["scores", "statistics"])


def get_score(entity: model.Base, user: model.User) -> int:
    # assert entity
    # assert user
    if not user or not user.user_id:
        return 0
    table, get_column = _get_table_info(entity)
    row = (
        db.session.query(table.score)
        .filter(get_column(table) == get_column(entity))
        .filter(table.user_id == user.user_id)
        .one_or_none()
    )
    return row[0] if row else 0


def get_post_scores_for_user(post_ids: list, user: model.User) -> dict:
    """
    Batch fetch user scores for multiple posts in a single query.
    Returns a dict mapping post_id -> score (or 0 if not scored).
    """
    if not post_ids or not user or not user.user_id:
        return {}

    rows = (
        db.session.query(model.PostScore.post_id, model.PostScore.score)
        .filter(model.PostScore.post_id.in_(post_ids))
        .filter(model.PostScore.user_id == user.user_id)
        .all()
    )
    return {row[0]: row[1] for row in rows}


def get_post_favorites_for_user(post_ids: list, user: model.User) -> set:
    """
    Batch fetch user favorites for multiple posts in a single query.
    Returns a set of post_ids that the user has favorited.
    """
    if not post_ids or not user or not user.user_id:
        return set()

    rows = (
        db.session.query(model.PostFavorite.post_id)
        .filter(model.PostFavorite.post_id.in_(post_ids))
        .filter(model.PostFavorite.user_id == user.user_id)
        .all()
    )
    return {row[0] for row in rows}


def set_score(entity: model.Base, user: model.User, score: int) -> None:
    from szurubooru.func import favorites

    # assert entity
    # assert user
    _ensure_user_id(user)
    if not score:
        delete_score(entity, user)
        try:
            favorites.unset_favorite(entity, user)
        except favorites.InvalidFavoriteTargetError:
            pass
        return
    if score not in (-1, 1):
        raise InvalidScoreValueError(
            "Score %r is invalid. Valid scores: %r." % (score, (-1, 1))
        )
    table_cls, get_column = _get_table_info(entity)
    column_name = get_column(table_cls).name
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    insert_stmt = pg_insert(table_cls.__table__).values(
        {
            column_name: get_column(entity),
            "user_id": user.user_id,
            "score": score,
            "time": now,
        }
    )
    insert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[column_name, "user_id"],
        set_={"score": score, "time": now},
    )
    db.session.execute(insert_stmt)
    _refresh_score_statistics(entity)
    db.session.expire(entity, ["scores", "statistics"])
    if score < 1:
        try:
            favorites.unset_favorite(entity, user)
        except favorites.InvalidFavoriteTargetError:
            pass
