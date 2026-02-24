from szurubooru.func import cache


def invalidate_search() -> None:
    cache.purge(scope=cache.SCOPE_SEARCH)


def invalidate_post_responses() -> None:
    cache.purge(scope=cache.SCOPE_POST_RESPONSE)


def invalidate_tag_responses() -> None:
    cache.purge(scope=cache.SCOPE_TAG_RESPONSE)


def invalidate_post_related() -> None:
    invalidate_search()
    invalidate_post_responses()


def invalidate_tag_related() -> None:
    invalidate_search()
    invalidate_post_responses()
    invalidate_tag_responses()
