from unittest.mock import patch

import pytest

from szurubooru import api, db, errors, model
from szurubooru.func import tags


@pytest.fixture(autouse=True)
def inject_config(config_injector):
    config_injector(
        {
            "privileges": {
                "tags:list": model.User.RANK_REGULAR,
                "tags:view": model.User.RANK_REGULAR,
            },
        }
    )


@pytest.fixture(autouse=True)
def clear_tag_list_cache():
    api.tag_api.clear_all_cached_tag_lists()
    yield
    api.tag_api.clear_all_cached_tag_lists()


def test_retrieving_multiple(user_factory, tag_factory, context_factory):
    tag1 = tag_factory(names=["t1"])
    tag2 = tag_factory(names=["t2"])
    db.session.add_all([tag2, tag1])
    db.session.flush()
    with patch("szurubooru.func.tags.serialize_tag"):
        tags.serialize_tag.return_value = "serialized tag"
        result = api.tag_api.get_tags(
            context_factory(
                params={"query": "", "offset": 0},
                user=user_factory(rank=model.User.RANK_REGULAR),
            )
        )
        assert result == {
            "query": "",
            "offset": 0,
            "limit": 100,
            "total": 2,
            "results": ["serialized tag", "serialized tag"],
        }


def test_trying_to_retrieve_multiple_without_privileges(
    user_factory, context_factory
):
    with pytest.raises(errors.AuthError):
        api.tag_api.get_tags(
            context_factory(
                params={"query": "", "offset": 0},
                user=user_factory(rank=model.User.RANK_ANONYMOUS),
            )
        )


def test_retrieving_single(user_factory, tag_factory, context_factory):
    db.session.add(tag_factory(names=["tag"]))
    db.session.flush()
    with patch("szurubooru.func.tags.serialize_tag"):
        tags.serialize_tag.return_value = "serialized tag"
        result = api.tag_api.get_tag(
            context_factory(user=user_factory(rank=model.User.RANK_REGULAR)),
            {"tag_name": "tag"},
        )
        assert result == "serialized tag"


def test_trying_to_retrieve_single_non_existing(user_factory, context_factory):
    with pytest.raises(tags.TagNotFoundError):
        api.tag_api.get_tag(
            context_factory(user=user_factory(rank=model.User.RANK_REGULAR)),
            {"tag_name": "-"},
        )


def test_trying_to_retrieve_single_without_privileges(
    user_factory, context_factory
):
    with pytest.raises(errors.AuthError):
        api.tag_api.get_tag(
            context_factory(user=user_factory(rank=model.User.RANK_ANONYMOUS)),
            {"tag_name": "-"},
        )


def test_retrieving_all_tags_uses_separate_minimal_and_full_cache(
    user_factory, context_factory
):
    calls = []

    def side_effect(ctx, _serializer):
        fields = tuple(ctx.get_param_as_list("fields", default=[]))
        calls.append(fields)
        return {
            "query": ctx.get_param_as_string("q", default=""),
            "offset": ctx.get_param_as_int("offset", default=0, min=0),
            "limit": ctx.get_param_as_int(
                "limit", default=100, min=1, max=5000
            ),
            "total": 0,
            "results": [{"fields": list(fields)}],
        }

    with patch.object(
        api.tag_api._search_executor,
        "execute_and_serialize",
        side_effect=side_effect,
    ):
        user = user_factory(rank=model.User.RANK_REGULAR)

        minimal_params = {
            "q": "sort:usages",
            "offset": 0,
            "limit": 5000,
            "fields": ["names", "usages", "category"],
        }
        full_params = {
            "q": "sort:usages",
            "offset": 0,
            "limit": 5000,
            "fields": [
                "names",
                "suggestions",
                "implications",
                "creationTime",
                "usages",
                "category",
            ],
        }

        api.tag_api.get_all_tags(
            context_factory(params=minimal_params, user=user)
        )
        api.tag_api.get_all_tags(context_factory(params=full_params, user=user))
        api.tag_api.get_all_tags(
            context_factory(params=minimal_params, user=user)
        )
        api.tag_api.get_all_tags(context_factory(params=full_params, user=user))

    assert calls == [
        ("names", "usages", "category"),
        (
            "names",
            "suggestions",
            "implications",
            "creationTime",
            "usages",
            "category",
        ),
    ]
