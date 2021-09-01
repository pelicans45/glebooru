from math import ceil
from queue import Queue
from typing import List

from szurubooru import model, search

_search_executor_config = search.configs.PostSearchConfig()
_search_executor = search.Executor(_search_executor_config)


def find_similar_posts(
    source_post: model.Post, limit: int, query_text: str = ''
) -> List[model.Post]:
    results = []
    # Sort tags in order of increasing post count, i.e. least to most popular
    # This will help yield results quicker
    source_tags = sorted(source_post.tags, key=lambda t: t.post_count)
    source_tag_count = len(source_tags)
    max_removals = source_tag_count - 1

    tags = source_tags
    for x in range(max_removals + 1):
        # prepare the current search, remove known results
        query = query_text + ' ' + ' '.join([t.first_name for t in tags])
        query += ' -id:%d' % source_post.post_id
        for r in results:
            query += ' -id:%d' % r.post_id

        # execute
        _, posts = _search_executor.execute(query, 0, limit - len(results))

        # update results
        for p in posts:
            results.append(p)
            if len(results) >= limit:
                break

        # remove the least popular tag
        if len(tags) <= 1:
            break
        tags = tags[1:]

    return results
