import logging
from typing import Any, Dict

from szurubooru import model, rest, search
from szurubooru.func import auth, serialization, users, versions
from szurubooru import errors

_search_executor = search.Executor(search.configs.UserSearchConfig())

USERNAME_BLACKLIST = [
    "fagg",
    "nigg",
    "jew",
    "kike",
    "cunt",
    "jeet",
    "tran"
]


def _serialize(
    ctx: rest.Context, user: model.User, **kwargs: Any
) -> rest.Response:
    return users.serialize_user(
        user,
        ctx.user,
        options=serialization.get_serialization_options(ctx),
        **kwargs
    )


@rest.routes.get("/users/?")
def get_users(
    ctx: rest.Context, _params: Dict[str, str] = {}
) -> rest.Response:
    auth.verify_privilege(ctx.user, "users:list")
    return _search_executor.execute_and_serialize(
        ctx, lambda user: _serialize(ctx, user)
    )

@rest.routes.post("/users/?")
def create_user(
    ctx: rest.Context, _params: Dict[str, str] = {}
) -> rest.Response:
    if ctx.user.user_id is None:
        auth.verify_privilege(ctx.user, "users:create:self")
    else:
        auth.verify_privilege(ctx.user, "users:create:any")


    logging.info("ctx: %s", ctx._headers)

    name = ctx.get_param_as_string("name")
    if any(s in name for s in USERNAME_BLACKLIST):
        raise errors.ValidationError("Invalid username")

    password = ctx.get_param_as_string("password")
    email = ctx.get_param_as_string("email", default="")
    user = users.create_user(name, password, email)
    if ctx.has_param("rank"):
        users.update_user_rank(user, ctx.get_param_as_string("rank"), ctx.user)
    if ctx.has_param("avatarStyle"):
        users.update_user_avatar(
            user,
            ctx.get_param_as_string("avatarStyle"),
            ctx.get_file("avatar", default=b""),
        )

    # get the IP from the ctx headers and log the IP
    ip = ctx.get_header("X-Real-Ip")
    logging.info("[REGISTRATION] User %s created by %s", name, ip)
    ctx.session.add(user)
    ctx.session.commit()

    return _serialize(ctx, user, force_show_email=True)


@rest.routes.get("/user/(?P<user_name>[^/]+)/?")
def get_user(ctx: rest.Context, params: Dict[str, str]) -> rest.Response:
    user = users.get_user_by_name(params["user_name"])
    if ctx.user.user_id != user.user_id:
        auth.verify_privilege(ctx.user, "users:view")
    return _serialize(ctx, user)


@rest.routes.put("/user/(?P<user_name>[^/]+)/?")
def update_user(ctx: rest.Context, params: Dict[str, str]) -> rest.Response:
    user = users.get_user_by_name(params["user_name"])
    versions.verify_version(user, ctx)
    versions.bump_version(user)
    infix = "self" if ctx.user.user_id == user.user_id else "any"

    if infix == "any" and user.rank == model.User.RANK_ADMINISTRATOR and ctx.user.rank != model.User.RANK_ADMINISTRATOR:
        raise errors.ValidationError("Cannot edit administrator")
    if infix == "any" and user.rank == model.User.RANK_MODERATOR and not (ctx.user.rank == model.User.RANK_ADMINISTRATOR or ctx.user.rank == model.User.RANK_MODERATOR):
        raise errors.ValidationError("Cannot edit moderator")
    if ctx.has_param("name"):
        auth.verify_privilege(ctx.user, "users:edit:%s:name" % infix)
        users.update_user_name(user, ctx.get_param_as_string("name"))
    if ctx.has_param("password"):
        auth.verify_privilege(ctx.user, "users:edit:%s:pass" % infix)
        users.update_user_password(user, ctx.get_param_as_string("password"))
    if ctx.has_param("email"):
        auth.verify_privilege(ctx.user, "users:edit:%s:email" % infix)
        users.update_user_email(user, ctx.get_param_as_string("email"))
    if ctx.has_param("rank"):
        auth.verify_privilege(ctx.user, "users:edit:%s:rank" % infix)
        users.update_user_rank(user, ctx.get_param_as_string("rank"), ctx.user)
    if ctx.has_param("avatarStyle"):
        auth.verify_privilege(ctx.user, "users:edit:%s:avatar" % infix)
        users.update_user_avatar(
            user,
            ctx.get_param_as_string("avatarStyle"),
            ctx.get_file("avatar", default=b""),
        )
    ctx.session.commit()
    return _serialize(ctx, user)


@rest.routes.delete("/user/(?P<user_name>[^/]+)/?")
def delete_user(ctx: rest.Context, params: Dict[str, str]) -> rest.Response:
    user = users.get_user_by_name(params["user_name"])
    versions.verify_version(user, ctx)
    infix = "self" if ctx.user.user_id == user.user_id else "any"
    auth.verify_privilege(ctx.user, "users:delete:%s" % infix)
    ctx.session.delete(user)
    ctx.session.commit()
    return {}
