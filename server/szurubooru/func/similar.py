from typing import List

import sqlalchemy as sa

from szurubooru import db, model, search
from szurubooru.func import posts as posts_func

#_search_executor_config = search.configs.PostSearchConfig()
#_search_executor = search.Executor(_search_executor_config)


# TODO(hunternif): this ignores the query, e.g. rating.
# (But we're actually using a "similar" search query on the client anyway.)
def find_similar_posts(
    source_post: model.Post, limit: int, query_text: str = ''
) -> List[model.Post]:
    if not source_post:
        return []

    pt_source = sa.orm.aliased(model.PostTag)
    pt_match = sa.orm.aliased(model.PostTag)

    rows = (
        db.session.query(
            pt_match.post_id.label("post_id"),
            sa.func.count(pt_match.tag_id).label("similarity"),
        )
        .join(pt_source, pt_source.tag_id == pt_match.tag_id)
        .filter(pt_source.post_id == source_post.post_id)
        .filter(pt_match.post_id != source_post.post_id)
        .group_by(pt_match.post_id)
        .order_by(sa.func.count(pt_match.tag_id).desc())
        .order_by(pt_match.post_id.desc())
        .limit(limit)
        .all()
    )
    if not rows:
        return []

    post_ids = [row.post_id for row in rows]
    posts = posts_func.get_posts_by_ids(post_ids)
    posts_by_id = {post.post_id: post for post in posts}
    return [posts_by_id[post_id] for post_id in post_ids if post_id in posts_by_id]
