from szurubooru.rest import middleware
from szurubooru.search.configs import util as search_util


@middleware.pre_hook
def clear_search_caches(_ctx) -> None:
    search_util.clear_tag_id_cache()


@middleware.post_hook
def clear_search_caches_after(_ctx) -> None:
    search_util.clear_tag_id_cache()
