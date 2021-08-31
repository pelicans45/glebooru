from queue import Queue
from typing import List

from szurubooru import model, search

_search_executor_config = search.configs.PostSearchConfig()
_search_executor = search.Executor(_search_executor_config)

_max_removals = 3


def find_similar_posts(source_post: model.Post, limit: int) -> List[model.Post]:
    results = []
    queue = Queue()  # contains lists of tags to search
    queue.put(source_post.tags)
    source_tag_count = len(source_post.tags)

    while not queue.empty():
        # put follow-up searches on the queue
        last_tags = queue.get()
        tag_count = len(last_tags)
        if tag_count > 1 and tag_count > source_tag_count - _max_removals:
            for removed_tag in last_tags:
                next_search = list(filter(lambda t: t != removed_tag, last_tags))
                queue.put(next_search)

        # prepare the current search, remove known results
        query = ' '.join([t.first_name for t in last_tags])
        query += ' -id:%d' % source_post.post_id
        for r in results:
            query += ' -id:%d' % r.post_id

        # execute
        _, posts = _search_executor.execute(query, 0, limit - len(results))

        # update results
        for p in posts:
            results.append(p)
            if len(results) >= limit:
                return results

    return results
