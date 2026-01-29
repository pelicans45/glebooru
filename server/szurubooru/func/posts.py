import hmac
import io
import logging
from datetime import datetime, UTC
from typing import Any, Callable, Dict, List, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy.event import listens_for

from szurubooru import config, db, errors, model, rest
from szurubooru.func import (
    comments,
    files,
    image_hash,
    images,
    mime,
    pools,
    scores,
    serialization,
    snapshots,
    tags,
    users,
    util,
)
from szurubooru.func.image_hash import NpMatrix
from szurubooru.log import logger

EMPTY_PIXEL = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00"
    b"\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00"
    b"\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
)


class PostNotFoundError(errors.NotFoundError):
    pass


class PostAlreadyFeaturedError(errors.ValidationError):
    pass


class PostAlreadyUploadedError(errors.ValidationError):
    def __init__(self, other_post_id: int) -> None:
        super().__init__(
            "File already uploaded (@%d)" % other_post_id,
            {
                # "otherPostUrl": get_post_content_url(other_post),
                "otherPostId": other_post_id,
            },
        )


class InvalidPostIdError(errors.ValidationError):
    pass


class InvalidPostSafetyError(errors.ValidationError):
    pass


class InvalidPostSourceError(errors.ValidationError):
    pass


class InvalidPostContentError(errors.ValidationError):
    pass


class InvalidPostRelationError(errors.ValidationError):
    pass


class InvalidPostNoteError(errors.ValidationError):
    pass


class InvalidPostFlagError(errors.ValidationError):
    pass


SAFETY_MAP = {
    model.Post.SAFETY_SAFE: "safe",
    model.Post.SAFETY_SKETCHY: "sketchy",
    model.Post.SAFETY_UNSAFE: "unsafe",
}

TYPE_MAP = {
    model.Post.TYPE_IMAGE: "image",
    model.Post.TYPE_ANIMATION: "animation",
    model.Post.TYPE_VIDEO: "video",
    model.Post.TYPE_AUDIO: "audio",
    model.Post.TYPE_FLASH: "flash",
}

FLAG_MAP = {
    model.Post.FLAG_LOOP: "loop",
    model.Post.FLAG_SOUND: "sound",
}


def get_post_security_hash(id: int) -> str:
    return hmac.new(
        config.config["secret"].encode("utf8"),
        msg=str(id).encode("utf-8"),
        digestmod="md5",
    ).hexdigest()[0:16]


def _get_post_security_hash_cached(post: model.Post) -> str:
    cached = getattr(post, "_security_hash", None)
    if cached is None:
        cached = get_post_security_hash(post.post_id)
        setattr(post, "_security_hash", cached)
    return cached


def get_post_content_url(post: model.Post) -> str:
    # assert post
    base_url = config.config.get("data_url") or ""
    if base_url and not base_url.endswith("/"):
        base_url += "/"
    extension = mime.get_extension(post.mime_type) or "dat"
    security_hash = _get_post_security_hash_cached(post)
    return f"{base_url}posts/{post.post_id}_{security_hash}.{extension}"



def get_post_thumbnail_extension(post: model.Post) -> str:
    if post.mime_type == "image/gif":
        return "gif"
    return "jpg"


def get_post_thumbnail_url(post: model.Post) -> str:
    # assert post
    base_url = config.config.get("data_url") or ""
    if base_url and not base_url.endswith("/"):
        base_url += "/"
    security_hash = _get_post_security_hash_cached(post)
    return (
        f"{base_url}generated-thumbnails/"
        f"{post.post_id}_{security_hash}.{get_post_thumbnail_extension(post)}"
    )


def get_post_content_path(post: model.Post) -> str:
    # assert post
    # assert post.post_id
    extension = mime.get_extension(post.mime_type) or "dat"
    security_hash = _get_post_security_hash_cached(post)
    return f"posts/{post.post_id}_{security_hash}.{extension}"


def get_post_thumbnail_path(post: model.Post) -> str:
    # assert post
    security_hash = _get_post_security_hash_cached(post)
    return (
        f"generated-thumbnails/{post.post_id}_{security_hash}."
        f"{get_post_thumbnail_extension(post)}"
    )


def get_post_thumbnail_backup_path(post: model.Post) -> str:
    # assert post
    security_hash = _get_post_security_hash_cached(post)
    return f"posts/custom-thumbnails/{post.post_id}_{security_hash}.dat"


def _get_thumbnail_min_file_size() -> int:
    return int(config.config.get("thumbnails", {}).get("min_file_size", 0))


def _get_thumbnail_dimensions() -> Tuple[int, int]:
    thumbnails = config.config.get("thumbnails", {})
    return (
        int(thumbnails.get("post_width", 300)),
        int(thumbnails.get("post_height", 300)),
    )


def serialize_note(note: model.PostNote) -> rest.Response:
    # assert note
    return {
        "polygon": note.polygon,
        "text": note.text,
    }


class PostSerializer(serialization.BaseSerializer):
    def __init__(
        self,
        post: model.Post,
        auth_user: model.User,
        preloaded_scores: Optional[Dict[int, int]] = None,
        preloaded_favorites: Optional[set] = None,
        preloaded_score_sums: Optional[Dict[int, int]] = None,
        preloaded_favorite_counts: Optional[Dict[int, int]] = None,
        preloaded_comment_counts: Optional[Dict[int, int]] = None,
        preloaded_tag_counts: Optional[Dict[int, int]] = None,
        preloaded_relations: Optional[Dict[int, List]] = None,
    ) -> None:
        self.post = post
        self.auth_user = auth_user
        # Pre-fetched data to avoid N+1 queries
        self._preloaded_scores = preloaded_scores
        self._preloaded_favorites = preloaded_favorites
        self._preloaded_score_sums = preloaded_score_sums
        self._preloaded_favorite_counts = preloaded_favorite_counts
        self._preloaded_comment_counts = preloaded_comment_counts
        self._preloaded_tag_counts = preloaded_tag_counts
        self._preloaded_relations = preloaded_relations

    def _serializers(self) -> Dict[str, Callable[[], Any]]:
        return {
            "id": self.serialize_id,
            "version": self.serialize_version,
            "creationTime": self.serialize_creation_time,
            "lastEditTime": self.serialize_last_edit_time,
            "safety": self.serialize_safety,
            "source": self.serialize_source,
            "type": self.serialize_type,
            "mimeType": self.serialize_mime,
            "checksum": self.serialize_checksum,
            "checksumMD5": self.serialize_checksum_md5,
            "fileSize": self.serialize_file_size,
            "canvasWidth": self.serialize_canvas_width,
            "canvasHeight": self.serialize_canvas_height,
            "duration": self.serialize_duration,
            "contentUrl": self.serialize_content_url,
            "thumbnailUrl": self.serialize_thumbnail_url,
            "flags": self.serialize_flags,
            "tags": self.serialize_tags,
            "tagsBasic": self.serialize_tags_basic,
            "relations": self.serialize_relations,
            "user": self.serialize_user,
            "score": self.serialize_score,
            "ownScore": self.serialize_own_score,
            "ownFavorite": self.serialize_own_favorite,
            "tagCount": self.serialize_tag_count,
            "favoriteCount": self.serialize_favorite_count,
            "commentCount": self.serialize_comment_count,
            "noteCount": self.serialize_note_count,
            "relationCount": self.serialize_relation_count,
            "featureCount": self.serialize_feature_count,
            "lastFeatureTime": self.serialize_last_feature_time,
            "favoritedBy": self.serialize_favorited_by,
            "notes": self.serialize_notes,
            "comments": self.serialize_comments,
            "pools": self.serialize_pools,
        }

    def serialize_id(self) -> Any:
        return self.post.post_id

    def serialize_version(self) -> Any:
        return self.post.version

    def serialize_creation_time(self) -> Any:
        return self.post.creation_time

    def serialize_last_edit_time(self) -> Any:
        return self.post.last_edit_time

    def serialize_safety(self) -> Any:
        return SAFETY_MAP[self.post.safety]

    def serialize_source(self) -> Any:
        return self.post.source

    def serialize_type(self) -> Any:
        return TYPE_MAP[self.post.type]

    def serialize_mime(self) -> Any:
        return self.post.mime_type

    def serialize_checksum(self) -> Any:
        return self.post.checksum

    def serialize_checksum_md5(self) -> Any:
        return self.post.checksum_md5

    def serialize_file_size(self) -> Any:
        return self.post.file_size

    def serialize_canvas_width(self) -> Any:
        return self.post.canvas_width

    def serialize_canvas_height(self) -> Any:
        return self.post.canvas_height

    def serialize_duration(self) -> Any:
        return self.post.duration

    def serialize_content_url(self) -> Any:
        return get_post_content_url(self.post)

    def serialize_thumbnail_url(self) -> Any:
        # Assume custom thumbnails are not used; avoid filesystem checks.
        if (
            (self.post.type == "image" or self.post.type == "animation")
            and self.post.file_size is not None
            and self.post.file_size
            < _get_thumbnail_min_file_size()
        ):
            return get_post_content_url(self.post)
        return get_post_thumbnail_url(self.post)

    def serialize_flags(self) -> Any:
        return self.post.flags

    def serialize_tags(self) -> Any:
        if not self.post.tags:
            return []
        result = []
        # Pass preloaded counts to sort_tags to avoid N+1 on tag.post_count
        for tag in tags.sort_tags(self.post.tags, self._preloaded_tag_counts):
            # Use preloaded tag counts if available to avoid N+1 queries
            if self._preloaded_tag_counts is not None:
                usages = self._preloaded_tag_counts.get(tag.tag_id, 0)
            else:
                usages = tag.post_count
            result.append({
                "names": [name.name for name in tag.names],
                "category": tag.category.name,
                "usages": usages,
            })
        return result

    def serialize_tags_basic(self) -> Any:
        if not self.post.tags:
            return []
        return [
            {
                "names": [name.name for name in tag.names],
                "category": tag.category.name,
            }
            for tag in tags.sort_tags(self.post.tags, self._preloaded_tag_counts)
        ]

    def serialize_relations(self) -> Any:
        # Use preloaded relations if available to avoid N+1 queries
        if self._preloaded_relations is not None:
            related_posts = self._preloaded_relations.get(self.post.post_id, [])
        else:
            # Fallback to per-post query
            relations = get_post_relations(self.post.post_id)
            if not relations:
                return []
            child_ids = list({rel.child_id for rel in relations})
            related_posts = get_posts_by_ids(child_ids)
        return sorted(
            [
                serialize_micro_post(post, self.auth_user)
                for post in related_posts
                if post is not None
            ],
            key=lambda post: post["id"],
        )

    def serialize_user(self) -> Any:
        return users.serialize_micro_user(self.post.user, self.auth_user)

    def serialize_score(self) -> Any:
        if self._preloaded_score_sums is not None:
            return self._preloaded_score_sums.get(self.post.post_id, 0)
        return self.post.score

    def serialize_own_score(self) -> Any:
        # Use pre-fetched score if available (batch optimization)
        if self._preloaded_scores is not None:
            return self._preloaded_scores.get(self.post.post_id, 0)
        return scores.get_score(self.post, self.auth_user)

    def serialize_own_favorite(self) -> Any:
        # Use pre-fetched favorites if available (batch optimization)
        if self._preloaded_favorites is not None:
            return self.post.post_id in self._preloaded_favorites
        return (
            len(
                [
                    user
                    for user in self.post.favorited_by
                    if user.user_id == self.auth_user.user_id
                ]
            )
            > 0
        )

    def serialize_tag_count(self) -> Any:
        return self.post.tag_count

    def serialize_favorite_count(self) -> Any:
        if self._preloaded_favorite_counts is not None:
            return self._preloaded_favorite_counts.get(self.post.post_id, 0)
        return self.post.favorite_count

    def serialize_comment_count(self) -> Any:
        if self._preloaded_comment_counts is not None:
            return self._preloaded_comment_counts.get(self.post.post_id, 0)
        return self.post.comment_count

    def serialize_note_count(self) -> Any:
        return self.post.note_count

    def serialize_relation_count(self) -> Any:
        return self.post.relation_count

    def serialize_feature_count(self) -> Any:
        return self.post.feature_count

    def serialize_last_feature_time(self) -> Any:
        return self.post.last_feature_time

    def serialize_favorited_by(self) -> Any:
        return [
            users.serialize_micro_user(rel.user, self.auth_user)
            for rel in self.post.favorited_by
        ]

    def serialize_notes(self) -> Any:
        return sorted(
            [serialize_note(note) for note in self.post.notes],
            key=lambda x: x["polygon"],
        )

    def serialize_comments(self) -> Any:
        if getattr(self.post, "_comments_sorted", False):
            ordered_comments = self.post.comments
        else:
            ordered_comments = sorted(
                self.post.comments, key=lambda comment: comment.creation_time
            )
        return [
            comments.serialize_comment(comment, self.auth_user)
            for comment in ordered_comments
        ]

    def serialize_pools(self) -> List[Any]:
        return [
            pools.serialize_micro_pool(pool)
            for pool in sorted(self.post.pools, key=lambda pool: pool.creation_time)
        ]


def serialize_post(
    post: Optional[model.Post],
    auth_user: model.User,
    options: List[str] = [],
    preloaded_scores: Optional[Dict[int, int]] = None,
    preloaded_favorites: Optional[set] = None,
    preloaded_score_sums: Optional[Dict[int, int]] = None,
    preloaded_favorite_counts: Optional[Dict[int, int]] = None,
    preloaded_comment_counts: Optional[Dict[int, int]] = None,
    preloaded_tag_counts: Optional[Dict[int, int]] = None,
    preloaded_relations: Optional[Dict[int, List]] = None,
) -> Optional[rest.Response]:
    if not post:
        return None

    # Pre-fetch data for single post if not provided (avoids N+1 queries)
    needs_tags = not options or "tags" in options or "tagsBasic" in options
    needs_relations = not options or "relations" in options
    needs_user = not options or "user" in options
    needs_notes = not options or "notes" in options
    needs_comments = not options or "comments" in options
    needs_own_score = not options or "ownScore" in options
    needs_own_favorite = not options or "ownFavorite" in options
    needs_favorited_by = not options or "favoritedBy" in options
    needs_pools = not options or "pools" in options
    needs_stats = not options or bool(
        {
            "score",
            "tagCount",
            "favoriteCount",
            "commentCount",
            "noteCount",
            "relationCount",
            "featureCount",
            "lastFeatureTime",
        }.intersection(options)
    )

    state = sa.orm.attributes.instance_state(post)

    need_user_load = needs_user and "user" not in state.dict
    need_stats_load = needs_stats and "statistics" not in state.dict
    stats_obj = post.statistics if "statistics" in state.dict else None

    if need_user_load or need_stats_load:
        row = (
            db.session.query(model.User, model.PostStatistics)
            .select_from(model.Post)
            .outerjoin(model.User, model.User.user_id == model.Post.user_id)
            .outerjoin(
                model.PostStatistics,
                model.PostStatistics.post_id == model.Post.post_id,
            )
            .filter(model.Post.post_id == post.post_id)
            .one_or_none()
        )
        user_obj, stats_obj = row if row else (None, None)
        if need_user_load:
            sa.orm.attributes.set_committed_value(post, "user", user_obj)
        if need_stats_load:
            sa.orm.attributes.set_committed_value(post, "statistics", stats_obj)

    if needs_comments and "comments" not in state.dict:
        if stats_obj is not None and getattr(stats_obj, "comment_count", 0) == 0:
            sa.orm.attributes.set_committed_value(post, "comments", [])
            post._comments_sorted = True
        else:
            comment_query = (
                db.session.query(model.Comment)
                .filter(model.Comment.post_id == post.post_id)
                .order_by(model.Comment.creation_time)
            )
            # Avoid eager-loading comment scores for anonymous users.
            if not auth_user or not auth_user.user_id:
                comment_query = comment_query.options(
                    sa.orm.lazyload(model.Comment.scores)
                )
            comment_list = comment_query.all()
            sa.orm.attributes.set_committed_value(post, "comments", comment_list)
            post._comments_sorted = True

    if needs_notes and "notes" not in state.dict:
        if stats_obj is not None and getattr(stats_obj, "note_count", 0) == 0:
            sa.orm.attributes.set_committed_value(post, "notes", [])
        else:
            note_list = (
                db.session.query(model.PostNote)
                .filter(model.PostNote.post_id == post.post_id)
                .all()
            )
            sa.orm.attributes.set_committed_value(post, "notes", note_list)

    if needs_favorited_by and "favorited_by" not in state.dict:
        if stats_obj is not None and getattr(stats_obj, "favorite_count", 0) == 0:
            sa.orm.attributes.set_committed_value(post, "favorited_by", [])

    if needs_pools and "_pools" not in state.dict:
        if stats_obj is not None and getattr(stats_obj, "pool_count", 0) == 0:
            sa.orm.attributes.set_committed_value(post, "_pools", [])

    if needs_tags and preloaded_tag_counts is None:
        if stats_obj is not None and getattr(stats_obj, "tag_count", 0) == 0:
            sa.orm.attributes.set_committed_value(post, "tags", [])
            preloaded_tag_counts = {}
        elif "tags" not in state.dict:
            tags_by_post, tag_counts = _batch_load_tags_for_posts([post.post_id])
            sa.orm.attributes.set_committed_value(
                post, "tags", tags_by_post.get(post.post_id, [])
            )
            preloaded_tag_counts = tag_counts
        elif post.tags:
            preloaded_tag_counts = {
                tag.tag_id: int(tag.post_count or 0) for tag in post.tags
            }

    if preloaded_relations is None and needs_relations:
        if stats_obj is not None and getattr(stats_obj, "relation_count", 0) == 0:
            preloaded_relations = {post.post_id: []}
        else:
            preloaded_relations = get_relations_for_posts([post.post_id])

    if needs_own_score and preloaded_scores is None:
        preloaded_scores = scores.get_post_scores_for_user([post.post_id], auth_user)

    if needs_own_favorite and preloaded_favorites is None:
        preloaded_favorites = scores.get_post_favorites_for_user(
            [post.post_id], auth_user
        )

    return PostSerializer(
        post,
        auth_user,
        preloaded_scores,
        preloaded_favorites,
        preloaded_score_sums,
        preloaded_favorite_counts,
        preloaded_comment_counts,
        preloaded_tag_counts,
        preloaded_relations,
    ).serialize(options)


def serialize_micro_post(
    post: model.Post, auth_user: model.User
) -> Optional[rest.Response]:
    return serialize_post(post, auth_user=auth_user, options=["id", "thumbnailUrl"])


def serialize_posts_batch(
    post_list: List[model.Post],
    auth_user: model.User,
    options: List[str] = [],
) -> List[rest.Response]:
    """
    Batch serialize multiple posts with optimized data fetching.
    Pre-fetches user scores, favorites, tag counts, and relations
    to avoid N+1 queries.
    """
    if not post_list:
        return []

    post_ids = [post.post_id for post in post_list]

    # Only pre-fetch data that will actually be used
    # If options is empty, all fields are serialized
    needs_score = not options or "ownScore" in options
    needs_favorite = not options or "ownFavorite" in options
    needs_tags = not options or "tags" in options or "tagsBasic" in options
    needs_relations = not options or "relations" in options
    needs_stats = not options or bool(
        {
            "score",
            "tagCount",
            "favoriteCount",
            "commentCount",
            "noteCount",
            "relationCount",
            "featureCount",
            "lastFeatureTime",
        }.intersection(options)
    )

    preloaded_scores = None
    preloaded_favorites = None
    preloaded_score_sums = None
    preloaded_favorite_counts = None
    preloaded_comment_counts = None
    preloaded_tag_counts = None
    preloaded_relations = None

    if needs_score:
        preloaded_scores = scores.get_post_scores_for_user(post_ids, auth_user)
    if needs_favorite:
        preloaded_favorites = scores.get_post_favorites_for_user(post_ids, auth_user)

    # Ensure statistics are loaded in batch when needed to avoid N+1 queries.
    if needs_stats or needs_tags:
        missing_stats_ids = []
        for post in post_list:
            state = sa.orm.attributes.instance_state(post)
            if "statistics" not in state.dict:
                missing_stats_ids.append(post.post_id)
        if missing_stats_ids:
            stats_rows = (
                db.session.query(model.PostStatistics)
                .filter(model.PostStatistics.post_id.in_(missing_stats_ids))
                .all()
            )
            stats_by_post = {stat.post_id: stat for stat in stats_rows}
            for post in post_list:
                state = sa.orm.attributes.instance_state(post)
                if "statistics" not in state.dict:
                    sa.orm.attributes.set_committed_value(
                        post, "statistics", stats_by_post.get(post.post_id)
                    )

    # Batch fetch tags and tag post counts
    if needs_tags:
        # Check if tags are already loaded on the first post
        first_post_state = sa.orm.attributes.instance_state(post_list[0])
        tags_already_loaded = 'tags' in first_post_state.dict

        if not tags_already_loaded:
            posts_with_tags = []
            posts_without_tags = []
            for post in post_list:
                state = sa.orm.attributes.instance_state(post)
                stats = state.dict.get("statistics")
                if stats is not None and getattr(stats, "tag_count", 0) == 0:
                    posts_without_tags.append(post)
                else:
                    posts_with_tags.append(post)

            tags_by_post = {}
            tag_counts = {}
            if posts_with_tags:
                # Batch load tags only for posts that actually have tags
                tags_by_post, tag_counts = _batch_load_tags_for_posts(
                    [post.post_id for post in posts_with_tags]
                )
                for post in posts_with_tags:
                    post_tags = tags_by_post.get(post.post_id, [])
                    sa.orm.attributes.set_committed_value(
                        post, 'tags', post_tags
                    )
            for post in posts_without_tags:
                sa.orm.attributes.set_committed_value(post, 'tags', [])
            preloaded_tag_counts = tag_counts
        else:
            # Tags already loaded; build counts from tag.statistics to avoid extra query
            tag_counts: Dict[int, int] = {}
            for post in post_list:
                for tag in post.tags:
                    tag_counts[tag.tag_id] = int(tag.post_count or 0)
            preloaded_tag_counts = tag_counts

    # Batch fetch relations
    if needs_relations:
        preloaded_relations = get_relations_for_posts(post_ids)

    # Serialize all posts with pre-fetched data
    return [
        serialize_post(
            post,
            auth_user,
            options,
            preloaded_scores,
            preloaded_favorites,
            preloaded_score_sums,
            preloaded_favorite_counts,
            preloaded_comment_counts,
            preloaded_tag_counts,
            preloaded_relations,
        )
        for post in post_list
    ]


def _batch_load_tags_for_posts(
    post_ids: List[int],
) -> Tuple[Dict[int, List[model.Tag]], Dict[int, int]]:
    """Load tags for multiple posts in a single query, plus tag usage counts."""
    if not post_ids:
        return {}, {}

    post_tags = (
        db.session.query(
            model.PostTag.post_id,
            model.Tag,
        )
        .join(model.Tag, model.PostTag.tag_id == model.Tag.tag_id)
        .join(model.Tag.statistics)
        .filter(model.PostTag.post_id.in_(post_ids))
        .options(
            sa.orm.contains_eager(model.Tag.statistics),
            sa.orm.joinedload(model.Tag.names),
            sa.orm.joinedload(model.Tag.category),
        )
        .all()
    )

    tags_by_post = {pid: [] for pid in post_ids}
    tag_counts: Dict[int, int] = {}
    for post_id, tag in post_tags:
        tags_by_post[post_id].append(tag)
        tag_counts[tag.tag_id] = int(tag.post_count or 0)

    return tags_by_post, tag_counts


def get_post_relations(post_id: int) -> List[model.Post]:
    # return db.session.query(model.PostRelation).filter(model.PostRelation.parent_id == post_id).all()
    return (
        db.session.query(model.PostRelation)
        .from_statement(sa.text("select * from post_relation where parent_id = :id"))
        .params(id=post_id)
        .all()
    )


def get_tag_post_counts(tag_ids: List[int]) -> Dict[int, int]:
    """Batch fetch post counts for multiple tags."""
    if not tag_ids:
        return {}
    result = (
        db.session.query(
            model.TagStatistics.tag_id,
            model.TagStatistics.usage_count,
        )
        .filter(model.TagStatistics.tag_id.in_(tag_ids))
        .all()
    )
    return {tag_id: int(count or 0) for tag_id, count in result}


def get_relations_for_posts(post_ids: List[int]) -> Dict[int, List[model.Post]]:
    """Batch fetch relations for multiple posts."""
    if not post_ids:
        return {}
    # Get all relations for these posts
    relations = (
        db.session.query(model.PostRelation)
        .filter(model.PostRelation.parent_id.in_(post_ids))
        .all()
    )
    if not relations:
        return {}

    # Group child_ids by parent
    parent_to_children: Dict[int, List[int]] = {}
    all_child_ids = set()
    for rel in relations:
        if rel.parent_id not in parent_to_children:
            parent_to_children[rel.parent_id] = []
        parent_to_children[rel.parent_id].append(rel.child_id)
        all_child_ids.add(rel.child_id)

    # Fetch all related posts in one query
    if all_child_ids:
        related_posts = get_posts_by_ids(list(all_child_ids))
        posts_by_id = {p.post_id: p for p in related_posts}
    else:
        posts_by_id = {}

    # Build result dict
    result: Dict[int, List[model.Post]] = {}
    for parent_id, child_ids in parent_to_children.items():
        result[parent_id] = [posts_by_id[cid] for cid in child_ids if cid in posts_by_id]

    return result


def get_post_count() -> int:
    stats = (
        db.session.query(model.DatabaseStatistics)
        .filter(model.DatabaseStatistics.id == True)  # noqa: E712
        .one_or_none()
    )
    if stats:
        return int(stats.post_count or 0)
    return db.session.query(sa.func.count(model.Post.post_id)).one()[0]


post_select_statement = sa.text("select * from post where id = :id")


def try_get_post_by_id(post_id: int) -> Optional[model.Post]:
    """Fetch post using raw SQL - fast but without eager loading."""
    return (
        db.session.query(model.Post)
        .from_statement(post_select_statement)
        .params(id=post_id)
        .first()
    )


def try_get_post_by_id_for_serialization(post_id: int) -> Optional[model.Post]:
    """Fetch post with eager loading for serialization (avoids N+1)."""
    return (
        db.session.query(model.Post)
        .filter(model.Post.post_id == post_id)
        .options(
            # Tags with names and categories (but not post_count - we batch that)
            sa.orm.joinedload(model.Post.statistics),
            sa.orm.subqueryload(model.Post.tags).subqueryload(model.Tag.names),
            sa.orm.subqueryload(model.Post.tags).joinedload(model.Tag.category),
            sa.orm.subqueryload(model.Post.tags).lazyload(model.Tag.implications),
            sa.orm.subqueryload(model.Post.tags).lazyload(model.Tag.suggestions),
            # Other relationships
            sa.orm.subqueryload(model.Post.favorited_by),
            sa.orm.subqueryload(model.Post.comments),
            sa.orm.subqueryload(model.Post.notes),
            sa.orm.subqueryload(model.Post._pools).joinedload(model.PoolPost.pool).joinedload(model.Pool.names),
            sa.orm.subqueryload(model.Post._pools).joinedload(model.PoolPost.pool).joinedload(model.Pool.category),
        )
        .first()
    )


def get_post_by_id(post_id: int) -> model.Post:
    post = try_get_post_by_id(post_id)
    if not post:
        raise PostNotFoundError("Post %r not found" % post_id)
    return post


def get_post_by_id_for_serialization(post_id: int) -> model.Post:
    """Fetch post with eager loading - use for API responses."""
    post = try_get_post_by_id_for_serialization(post_id)
    if not post:
        raise PostNotFoundError("Post %r not found" % post_id)
    return post


def get_posts_by_ids(ids: List[int], eager_load_tags: bool = False) -> List[model.Post]:
    if len(ids) == 0:
        return []
    query = db.session.query(model.Post).filter(model.Post.post_id.in_(ids))

    if eager_load_tags:
        query = query.options(
            # Tags with names and categories for efficient batch serialization
            sa.orm.subqueryload(model.Post.tags).subqueryload(model.Tag.names),
            sa.orm.subqueryload(model.Post.tags).joinedload(model.Tag.category),
            sa.orm.subqueryload(model.Post.tags).lazyload(model.Tag.implications),
            sa.orm.subqueryload(model.Post.tags).lazyload(model.Tag.suggestions),
        )

    posts = query.all()
    id_order = {v: k for k, v in enumerate(ids)}
    return sorted(posts, key=lambda post: id_order.get(post.post_id))


def try_get_current_post_feature() -> Optional[model.PostFeature]:
    return (
        db.session.query(model.PostFeature)
        .order_by(model.PostFeature.time.desc())
        .first()
    )


def try_get_featured_post() -> Optional[model.Post]:
    post_feature = try_get_current_post_feature()
    return post_feature.post if post_feature else None


TAG_IMPLICATIONS = {
    "bury": "character",
    "spikedog": "character",
    "glegle": "character",
    "flube": "character",
    "yosho": "character",
}

SITE_TAGS = {
    "bury.pink": "bury",
    "spikedog.school": "spikedog",
    "glegle.gallery": "glegle",
    "flube.supply": "flube",
    "yosho.io": "yosho",
    "politics.lol": "politics",
    "boymoders.com": "boymoder",
}


def add_extra_tags(host, tag_names):
    if not host:
        return
    site = config.config["sites"].get(host)
    if not site:
        return
    site_tag = site.get("query")
    if site_tag and site_tag not in tag_names:
        tag_names.append(site_tag)

    implications = site.get("implies", [])
    for implication in implications:
        if implication not in tag_names:
            tag_names.append(implication)

    for tag in tag_names:
        implication = TAG_IMPLICATIONS.get(tag)
        if implication and implication not in tag_names:
            tag_names.append(implication)


def create_post(
    content: bytes,
    tag_names: List[str],
    user: Optional[model.User],
    host: str = "",
    category_overrides: Optional[Dict[str, str]] = None,
) -> Tuple[model.Post, List[model.Tag]]:
    post = model.Post()
    post.safety = model.Post.SAFETY_SAFE
    post.user = user
    post.creation_time = datetime.now(UTC).replace(tzinfo=None)
    post.flags = []
    tag_names = tag_names or []

    post.type = ""
    post.checksum = ""
    post.mime_type = ""

    update_post_content(post, content)

    if post.type == model.Post.TYPE_ANIMATION and "gif" not in tag_names:
        tag_names.append("gif")
    elif post.type == model.Post.TYPE_VIDEO and "video" not in tag_names:
        tag_names.append("video")
    elif post.type == model.Post.TYPE_AUDIO and "audio" not in tag_names:
        tag_names.append("audio")

    add_extra_tags(host, tag_names)
    db.session.add(post)
    new_tags = update_post_tags(
        post, tag_names, category_overrides=category_overrides
    )
    return post, new_tags


def update_post_safety(post: model.Post, safety: str) -> None:
    # assert post
    safety = util.flip(SAFETY_MAP).get(safety, None)
    if not safety:
        raise InvalidPostSafetyError(
            "Safety can be either of %r" % list(SAFETY_MAP.values())
        )
    post.safety = safety


def update_post_source(post: model.Post, source: Optional[str]) -> None:
    # assert post
    if util.value_exceeds_column_size(source, model.Post.source):
        raise InvalidPostSourceError("Source is too long")
    post.source = source or None


@listens_for(model.Post, "after_insert")
def _after_post_insert(_mapper: Any, _connection: Any, post: model.Post) -> None:
    _sync_post_content(post)


@listens_for(model.Post, "after_update")
def _after_post_update(_mapper: Any, _connection: Any, post: model.Post) -> None:
    _sync_post_content(post)


@listens_for(model.Post, "before_delete")
def _before_post_delete(_mapper: Any, _connection: Any, post: model.Post) -> None:
    if post.post_id:
        if config.config["delete_source_files"]:
            files.delete(get_post_content_path(post))
            files.delete(get_post_thumbnail_path(post))


def _sync_post_content(post: model.Post) -> None:
    regenerate_thumb = False

    if hasattr(post, "__content"):
        content = getattr(post, "__content")
        files.save(get_post_content_path(post), content)
        delattr(post, "__content")
        regenerate_thumb = True

    if hasattr(post, "__thumbnail"):
        if getattr(post, "__thumbnail"):
            files.save(
                get_post_thumbnail_backup_path(post),
                getattr(post, "__thumbnail"),
            )
        else:
            files.delete(get_post_thumbnail_backup_path(post))
        delattr(post, "__thumbnail")
        regenerate_thumb = True

    if regenerate_thumb:
        generate_post_thumbnail(post)


def generate_alternate_formats(
    post: model.Post, content: bytes
) -> List[Tuple[model.Post, List[model.Tag]]]:
    # assert post
    # assert content
    new_posts = []
    if mime.is_animated_gif(content):
        tag_names = [tag.first_name for tag in post.tags]

        if config.config["convert"]["gif"]["to_mp4"]:
            mp4_post, new_tags = create_post(
                host="",
                content=images.Image(content).to_mp4(),
                tag_names=tag_names,
                user=post.user,
            )
            update_post_flags(mp4_post, ["loop"])
            update_post_safety(mp4_post, post.safety)
            update_post_source(mp4_post, post.source)
            new_posts += [(mp4_post, new_tags)]

        if config.config["convert"]["gif"]["to_webm"]:
            webm_post, new_tags = create_post(
                host="",
                content=images.Image(content).to_webm(),
                tag_names=tag_names,
                user=post.user,
            )
            update_post_flags(webm_post, ["loop"])
            update_post_safety(webm_post, post.safety)
            update_post_source(webm_post, post.source)
            new_posts += [(webm_post, new_tags)]

        db.session.flush()

        new_posts = [p for p in new_posts if p[0] is not None]

        new_relations = [p[0].post_id for p in new_posts]
        if len(new_relations) > 0:
            update_post_relations(post, new_relations)

    return new_posts


def get_default_flags(content: bytes) -> List[str]:
    # assert content
    ret = []
    if mime.is_video(mime.get_mime_type(content)):
        ret.append(model.Post.FLAG_LOOP)
        if images.Image(content).check_for_sound():
            ret.append(model.Post.FLAG_SOUND)
    return ret


def purge_post_signature(post: model.Post) -> None:
    """
    (
        db.session.query(model.PostSignature)
        .filter(model.PostSignature.post_id == post.post_id)
        .delete()
    )
    """
    db.session.execute(
        sa.text("delete from post_signature where post_id=:id"),
        {"id": post.post_id},
    )


def _build_post_signature(
    post: model.Post, unpacked_signature: NpMatrix
) -> model.PostSignature:
    packed_signature = image_hash.pack_signature(unpacked_signature)
    words = image_hash.generate_words(unpacked_signature)
    signature = model.PostSignature(
        post=post, signature=packed_signature, words=words
    )
    db.session.add(signature)
    return signature


def _generate_signature_bits(
    content: bytes, mime_type: Optional[str]
) -> Tuple[NpMatrix, bool]:
    try:
        return image_hash.generate_signature(content), False
    except errors.ProcessingError:
        ext = mime.get_extension(mime_type) if mime_type else None
        if ext in {"avif", "heic", "heif"}:
            logger.warning(
                "Falling back to placeholder image hash for %s", ext
            )
            unpacked_signature = image_hash.np.zeros(
                image_hash.SIG_NUMS, dtype=image_hash.np.uint8
            )
            return unpacked_signature, True
        raise


def _find_near_duplicate_post_id(
    signature: NpMatrix,
    exclude_post_id: Optional[int] = None,
    distance_cutoff: float = image_hash.DUPLICATE_DISTANCE_CUTOFF_STATIC,
) -> Optional[int]:
    matches = search_by_signature(
        signature,
        limit=50,
        distance_cutoff=distance_cutoff,
    )
    for _distance, post in matches:
        if post and post.post_id != exclude_post_id:
            return post.post_id
    return None


def generate_post_signature(
    post: model.Post, content: bytes
) -> Optional[model.PostSignature]:
    try:
        unpacked_signature, _is_placeholder = _generate_signature_bits(
            content, post.mime_type
        )
        return _build_post_signature(post, unpacked_signature)
    except errors.ProcessingError:
        if not config.config["allow_broken_uploads"]:
            raise InvalidPostContentError("Unable to generate image hash data")
        return None


def update_all_post_signatures() -> None:
    posts_to_hash = (
        db.session.query(model.Post)
        .filter(
            (model.Post.type == model.Post.TYPE_IMAGE)
            | (model.Post.type == model.Post.TYPE_ANIMATION)
        )
        .filter(model.Post.signature == None)  # noqa: E711
        .order_by(model.Post.post_id.asc())
        .all()
    )
    for post in posts_to_hash:
        try:
            content = files.get(get_post_content_path(post))
            if not content:
                logging.warning(
                    "Skipping signature for post %d: content missing",
                    post.post_id,
                )
                continue
            generate_post_signature(post, content)
            db.session.commit()
            # logging.info("Created Signature - Post %d", post.post_id)
        except Exception as ex:
            logging.exception(ex)


def update_all_md5_checksums() -> None:
    posts_to_hash = (
        db.session.query(model.Post)
        .filter(model.Post.checksum_md5 == None)  # noqa: E711
        .order_by(model.Post.post_id.asc())
        .all()
    )
    for post in posts_to_hash:
        try:
            content = files.get(get_post_content_path(post))
            if not content:
                logging.warning(
                    "Skipping md5 for post %d: content missing",
                    post.post_id,
                )
                continue
            post.checksum_md5 = util.get_md5(content)
            db.session.commit()
            # logging.info("Created MD5 - Post %d", post.post_id)
        except Exception as ex:
            logging.exception(ex)


def _convert_webp_to_supported(content: bytes) -> bytes:
    try:
        from PIL import Image
    except ImportError:
        raise InvalidPostContentError("Unhandled file type: 'image/webp'")

    try:
        with Image.open(io.BytesIO(content)) as image:
            if getattr(image, "is_animated", False) and getattr(
                image, "n_frames", 1
            ) > 1:
                frames = []
                durations = []
                for frame in range(image.n_frames):
                    image.seek(frame)
                    frame_rgba = image.convert("RGBA")
                    frames.append(frame_rgba)
                    durations.append(image.info.get("duration", 0))
                buffer = io.BytesIO()
                frames[0].save(
                    buffer,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=image.info.get("loop", 0),
                    disposal=image.info.get("disposal", 2),
                )
                return buffer.getvalue()
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA")
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()
    except Exception as ex:
        logging.exception(ex)
        raise InvalidPostContentError("Unable to convert WebP")


def update_post_content(
    post: model.Post, content: Optional[bytes], content_changed=False
) -> None:
    # assert post
    if not content:
        raise InvalidPostContentError("Post content missing")

    if mime.is_webp_content(content):
        content = _convert_webp_to_supported(content)
        content_changed = True

    update_signature = False
    post.mime_type = mime.get_mime_type(content)
    if mime.is_flash(post.mime_type):
        post.type = model.Post.TYPE_FLASH
    elif mime.is_image(post.mime_type):
        update_signature = True
        if mime.is_animated_gif(content):
            post.type = model.Post.TYPE_ANIMATION
        else:
            post.type = model.Post.TYPE_IMAGE
    elif mime.is_video(post.mime_type):
        post.type = model.Post.TYPE_VIDEO
    elif mime.is_audio(post.mime_type):
        post.type = model.Post.TYPE_AUDIO
    else:
        raise InvalidPostContentError("Unhandled file type: %r" % post.mime_type)

    post.checksum = util.get_sha1(content)
    post.checksum_md5 = util.get_md5(content)

    """
    other_post = (
        db.session.query(model.Post)
        .filter(model.Post.checksum == post.checksum)
        .filter(model.Post.post_id != post.post_id)
        .one_or_none()
    )
    """

    post_id = post.post_id
    if post_id is None:
        post_id = 0
    other_post_id = db.session.execute(
        sa.select(model.Post.post_id)
        .where(model.Post.checksum == post.checksum)
        .where(model.Post.post_id != post_id)
    ).scalar_one_or_none()

    if other_post_id and other_post_id != post.post_id:
        raise PostAlreadyUploadedError(other_post_id)

    if update_signature:
        if content_changed:
            purge_post_signature(post)
        try:
            unpacked_signature, is_placeholder = _generate_signature_bits(
                content, post.mime_type
            )
            if not is_placeholder:
                distance_cutoff = (
                    image_hash.DUPLICATE_DISTANCE_CUTOFF_ANIMATED
                    if post.type == model.Post.TYPE_ANIMATION
                    else image_hash.DUPLICATE_DISTANCE_CUTOFF_STATIC
                )
                other_post_id = _find_near_duplicate_post_id(
                    unpacked_signature,
                    post.post_id,
                    distance_cutoff=distance_cutoff,
                )
                if other_post_id:
                    raise PostAlreadyUploadedError(other_post_id)
            post.signature = _build_post_signature(post, unpacked_signature)
        except errors.ProcessingError as ex:
            logging.exception(ex)
            if not config.config["allow_broken_uploads"]:
                raise InvalidPostContentError(
                    "Unable to process image signature"
                ) from ex
            post.signature = None

    post.file_size = len(content)
    try:
        if post.type in (model.Post.TYPE_IMAGE, model.Post.TYPE_ANIMATION):
            post.canvas_width, post.canvas_height = images.get_image_dimensions(
                content
            )
            post.duration = None
        else:
            image = images.Image(content)
            post.canvas_width = image.width
            post.canvas_height = image.height
            if post.type in (model.Post.TYPE_VIDEO, model.Post.TYPE_AUDIO):
                post.duration = (
                    int(round(image.duration)) if image.duration > 0 else None
                )
            else:
                post.duration = None
    except errors.ProcessingError as ex:
        logging.exception(ex)
        if mime.is_heif(post.mime_type):
            post.canvas_width = None
            post.canvas_height = None
            post.duration = None
        elif not config.config["allow_broken_uploads"]:
            raise InvalidPostContentError("Unable to process image metadata")
        else:
            post.canvas_width = None
            post.canvas_height = None
            post.duration = None
    except Exception as ex:
        if mime.is_heif(post.mime_type):
            logging.exception(ex)
            post.canvas_width = None
            post.canvas_height = None
            post.duration = None
        else:
            raise
    if (post.canvas_width is not None and post.canvas_width <= 0) or (
        post.canvas_height is not None and post.canvas_height <= 0
    ):
        if not config.config["allow_broken_uploads"]:
            raise InvalidPostContentError(
                "Invalid image dimensions returned during processing"
            )
        else:
            post.canvas_width = None
            post.canvas_height = None
    setattr(post, "__content", content)


def update_post_thumbnail(post: model.Post, content: Optional[bytes] = None) -> None:
    # assert post
    setattr(post, "__thumbnail", content)


def generate_post_thumbnail(post: model.Post) -> None:
    # assert post

    backup_path = get_post_thumbnail_backup_path(post)
    has_custom_thumbnail = files.has(backup_path)

    if not has_custom_thumbnail:
        if (
            (post.type == "image" or post.type == "animation")
            and post.file_size is not None
            and post.file_size
            < _get_thumbnail_min_file_size()
        ):
            return

        if post.type == "audio":
            return

    if has_custom_thumbnail:
        content = files.get(backup_path)
    else:
        content = files.get(get_post_content_path(post))
    try:
        # assert content
        thumb_width, thumb_height = _get_thumbnail_dimensions()
        if get_post_thumbnail_extension(post) == "gif":
            image = images.Image(content)
            thumbnail_content = image.to_gif_thumbnail(thumb_width, thumb_height)
        elif post.type == model.Post.TYPE_IMAGE:
            thumbnail_content = images.resize_image_to_jpeg(
                content, thumb_width, thumb_height
            )
        else:
            image = images.Image(content)
            image.resize_fill(thumb_width, thumb_height)
            thumbnail_content = image.to_jpeg()
        files.save(get_post_thumbnail_path(post), thumbnail_content)
    except errors.ProcessingError:
        files.save(get_post_thumbnail_path(post), EMPTY_PIXEL)


def update_post_tags(
    post: model.Post,
    tag_names: List[str],
    category_overrides: Optional[Dict[str, str]] = None,
) -> List[model.Tag]:
    # assert post
    existing_tags, new_tags = tags.get_or_create_tags_by_names(
        tag_names, category_overrides
    )
    all_tags = existing_tags + new_tags

    state = sa.inspect(post)
    if state.transient:
        post.tags = all_tags
        return new_tags

    needs_flush = post.post_id is None or any(
        tag.tag_id is None for tag in new_tags
    )
    if needs_flush:
        db.session.flush()

    new_tag_ids = {tag.tag_id for tag in all_tags}
    if "tags" in state.dict:
        old_tag_ids = {tag.tag_id for tag in state.dict["tags"]}
    else:
        old_tag_ids = {
            tag_id
            for (tag_id,) in db.session.execute(
                sa.select(model.PostTag.tag_id).where(
                    model.PostTag.post_id == post.post_id
                )
            )
        }

    to_remove = old_tag_ids - new_tag_ids
    to_add = new_tag_ids - old_tag_ids

    if to_remove:
        db.session.execute(
            sa.text(
                "DELETE FROM post_tag "
                "WHERE post_id = :post_id "
                "AND tag_id = ANY(CAST(:tag_ids AS int[]))"
            ),
            {"post_id": post.post_id, "tag_ids": list(to_remove)},
        )

    if to_add:
        db.session.execute(
            sa.text(
                "INSERT INTO post_tag (post_id, tag_id) "
                "SELECT :post_id, unnest(CAST(:tag_ids AS int[])) "
                "ON CONFLICT DO NOTHING"
            ),
            {"post_id": post.post_id, "tag_ids": list(to_add)},
        )

    sa.orm.attributes.set_committed_value(post, "tags", all_tags)
    return new_tags


def update_post_relations(post: model.Post, new_post_ids: List[int]) -> None:
    # assert post
    try:
        new_post_ids = [int(id) for id in new_post_ids]
    except ValueError:
        raise InvalidPostRelationError("A relation must be a numeric post ID")
    old_posts = list(post.relations)
    old_post_ids = [int(p.post_id) for p in old_posts]
    if new_post_ids:
        new_posts = (
            db.session.query(model.Post)
            .filter(model.Post.post_id.in_(new_post_ids))
            .all()
        )
    else:
        new_posts = []
    if len(new_posts) != len(new_post_ids):
        raise InvalidPostRelationError("One of relations does not exist")
    if post.post_id in new_post_ids:
        raise InvalidPostRelationError("Post cannot relate to itself")

    relations_to_del = [p for p in old_posts if p.post_id not in new_post_ids]
    relations_to_add = [p for p in new_posts if p.post_id not in old_post_ids]
    for relation in relations_to_del:
        if post in relation.relations:
            relation.relations.remove(post)
        if relation in post.relations:
            post.relations.remove(relation)
    for relation in relations_to_add:
        if relation not in post.relations:
            post.relations.append(relation)
        if post not in relation.relations:
            relation.relations.append(post)


def update_post_notes(post: model.Post, notes: Any) -> None:
    # assert post
    post.notes = []
    for note in notes:
        for field in ("polygon", "text"):
            if field not in note:
                raise InvalidPostNoteError("Note is missing %r field" % field)
        if not note["text"]:
            raise InvalidPostNoteError("A note's text cannot be empty")
        if not isinstance(note["polygon"], (list, tuple)):
            raise InvalidPostNoteError("A note's polygon must be a list of points")
        if len(note["polygon"]) < 3:
            raise InvalidPostNoteError("A note's polygon must have at least 3 points")
        for point in note["polygon"]:
            if not isinstance(point, (list, tuple)):
                raise InvalidPostNoteError(
                    "A note's polygon point must be a list of length 2"
                )
            if len(point) != 2:
                raise InvalidPostNoteError(
                    "A point in note's polygon must have two coordinates"
                )
            try:
                pos_x = float(point[0])
                pos_y = float(point[1])
                if not 0 <= pos_x <= 1 or not 0 <= pos_y <= 1:
                    raise InvalidPostNoteError(
                        "All points must fit in the image (0..1 range)"
                    )
            except ValueError:
                raise InvalidPostNoteError("A point in note's polygon must be numeric")
        if util.value_exceeds_column_size(note["text"], model.PostNote.text):
            raise InvalidPostNoteError("Note text is too long")
        post.notes.append(
            model.PostNote(polygon=note["polygon"], text=str(note["text"]))
        )


def update_post_flags(post: model.Post, flags: List[str]) -> None:
    # assert post
    target_flags = []
    for flag in flags:
        flag = util.flip(FLAG_MAP).get(flag, None)
        if not flag:
            raise InvalidPostFlagError(
                "Flag must be one of %r" % list(FLAG_MAP.values())
            )
        target_flags.append(flag)
    post.flags = target_flags


def feature_post(post: model.Post, user: Optional[model.User]) -> None:
    # assert post
    if user and not user.name:
        user = None
    post_feature = model.PostFeature()
    post_feature.time = datetime.now(UTC).replace(tzinfo=None)
    post_feature.post = post
    post_feature.user = user
    db.session.add(post_feature)


def delete(post: model.Post) -> None:
    # assert post
    db.session.delete(post)


def merge_posts(
    source_post: model.Post,
    target_post: model.Post,
    replace_content: bool = False,
) -> None:
    # assert source_post
    # assert target_post
    if source_post.post_id == target_post.post_id:
        raise InvalidPostRelationError("Cannot merge post with itself")

    def merge_tables(
        table: model.Base,
        anti_dup_func: Optional[Callable[[model.Base, model.Base], bool]],
        source_post_id: int,
        target_post_id: int,
    ) -> None:
        alias1 = table
        alias2 = sa.orm.aliased(table)
        update_stmt = sa.sql.expression.update(alias1).where(
            alias1.post_id == source_post_id
        )

        if anti_dup_func is not None:
            update_stmt = update_stmt.where(
                ~sa.exists()
                .where(anti_dup_func(alias1, alias2))
                .where(alias2.post_id == target_post_id)
            )

        update_stmt = update_stmt.values(post_id=target_post_id)
        db.session.execute(
            update_stmt, execution_options={"synchronize_session": "fetch"}
        )

    def merge_tags(source_post_id: int, target_post_id: int) -> None:
        merge_tables(
            model.PostTag,
            lambda alias1, alias2: alias1.tag_id == alias2.tag_id,
            source_post_id,
            target_post_id,
        )

    def merge_scores(source_post_id: int, target_post_id: int) -> None:
        merge_tables(
            model.PostScore,
            lambda alias1, alias2: alias1.user_id == alias2.user_id,
            source_post_id,
            target_post_id,
        )

    def merge_favorites(source_post_id: int, target_post_id: int) -> None:
        merge_tables(
            model.PostFavorite,
            lambda alias1, alias2: alias1.user_id == alias2.user_id,
            source_post_id,
            target_post_id,
        )

    def merge_comments(source_post_id: int, target_post_id: int) -> None:
        merge_tables(model.Comment, None, source_post_id, target_post_id)

    def merge_relations(source_post_id: int, target_post_id: int) -> None:
        alias1 = model.PostRelation
        alias2 = sa.orm.aliased(model.PostRelation)
        update_stmt = (
            sa.sql.expression.update(alias1)
            .where(alias1.parent_id == source_post_id)
            .where(alias1.child_id != target_post_id)
            .where(
                ~sa.exists()
                .where(alias2.child_id == alias1.child_id)
                .where(alias2.parent_id == target_post_id)
            )
            .values(parent_id=target_post_id)
        )
        db.session.execute(
            update_stmt.execution_options(synchronize_session=False)
        )

        update_stmt = (
            sa.sql.expression.update(alias1)
            .where(alias1.child_id == source_post_id)
            .where(alias1.parent_id != target_post_id)
            .where(
                ~sa.exists()
                .where(alias2.parent_id == alias1.parent_id)
                .where(alias2.child_id == target_post_id)
            )
            .values(child_id=target_post_id)
        )
        db.session.execute(
            update_stmt.execution_options(synchronize_session=False)
        )

    merge_tags(source_post.post_id, target_post.post_id)
    merge_comments(source_post.post_id, target_post.post_id)
    merge_scores(source_post.post_id, target_post.post_id)
    merge_favorites(source_post.post_id, target_post.post_id)
    merge_relations(source_post.post_id, target_post.post_id)

    def transfer_flags(source_post_id: int, target_post_id: int) -> None:
        target = get_post_by_id(target_post_id)
        source = get_post_by_id(source_post_id)
        target.flags = source.flags
        db.session.flush()

    content = None
    if replace_content:
        content = files.get(get_post_content_path(source_post))
        transfer_flags(source_post.post_id, target_post.post_id)

    # fixes unknown issue with SA's cascade deletions
    purge_post_signature(source_post)
    delete(source_post)
    db.session.flush()

    if content is not None:
        update_post_content(target_post, content, content_changed=True)


def search_by_image_exact(image_content: bytes) -> Optional[model.Post]:
    checksum = util.get_sha1(image_content)

    return (
        db.session.query(model.Post)
        .from_statement(sa.text("select * from post where checksum=:checksum"))
        .params(checksum=checksum)
        .first()
    )
    return (
        db.session.query(model.Post)
        .filter(model.Post.checksum == checksum)
        .one_or_none()
    )


def search_by_image(image_content: bytes) -> List[Tuple[float, model.Post]]:
    query_signature = image_hash.generate_signature(image_content)
    return search_by_signature(query_signature)


def search_by_signature(
    signature: NpMatrix,
    limit: int = 100,
    distance_cutoff: float = image_hash.DISTANCE_CUTOFF,
    query: str = None,
) -> List[Tuple[float, model.Post]]:
    query_words = image_hash.generate_words(signature)
    """
    The unnest function is used here to expand one row containing the 'words'
    array into multiple rows each containing a singular word.

    Documentation of the unnest function can be found here:
    https://www.postgresql.org/docs/9.2/functions-array.html
    """

    dbquery = """
    SELECT s.post_id, s.signature, count(a.query) AS score
    FROM post_signature AS s
    CROSS JOIN LATERAL unnest(s.words, CAST(:q AS integer[])) AS a(word, query)
    {join_clause}
    WHERE s.words && CAST(:q AS integer[])
      AND a.word = a.query {where_clause}
    GROUP BY s.post_id
    ORDER BY score DESC LIMIT :limit;
    """

    join_clause = ""
    where_clause = ""
    params = {"q": query_words, "limit": limit}

    if query:
        tag = tags.try_get_tag_by_name(query)
        if not tag:
            return []
        join_clause = "JOIN post_tag pt ON s.post_id = pt.post_id"
        where_clause = "AND pt.tag_id = :tag_id"
        params["tag_id"] = tag.tag_id

    dbquery = dbquery.format(join_clause=join_clause, where_clause=where_clause)

    candidates = db.session.execute(sa.text(dbquery), params)
    data = tuple(
        zip(
            *[
                (post_id, image_hash.unpack_signature(packedsig))
                for post_id, packedsig, score in candidates
            ]
        )
    )
    if not data:
        return []

    candidate_post_ids, sigarray = data
    distances = image_hash.normalized_distance(sigarray, signature)

    # Filter by distance threshold first, then batch fetch posts (avoids N+1)
    matching = [
        (pid, dist)
        for pid, dist in zip(candidate_post_ids, distances)
        if dist < distance_cutoff
    ]
    if not matching:
        return []

    post_ids = [pid for pid, _ in matching]
    posts_map = {p.post_id: p for p in get_posts_by_ids(post_ids)}

    return [
        (dist, posts_map.get(pid))
        for pid, dist in matching
        if posts_map.get(pid) is not None
    ]
