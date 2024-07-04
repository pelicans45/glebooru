import html
import re
from typing import Dict, Optional
from urllib.parse import quote
from pathlib import Path

from szurubooru import config, model, rest
from szurubooru.func import auth, posts, serialization

current_dir = Path(__file__).parent.resolve()
index_html = (current_dir / "../../index.html").read_text()

def _index_path(params: Dict[str, str]) -> int:
    try:
        return params["path"]
    except (TypeError, ValueError):
        raise posts.InvalidPostIdError(
            "Invalid post ID"
        )


def _get_post(post_id: int) -> model.Post:
    return posts.get_post_by_id(post_id)


def _get_post_id(match: re.Match) -> int:
    post_id = match.group("post_id")
    try:
        return int(post_id)
    except (TypeError, ValueError):
        raise posts.InvalidPostIdError(
            "Invalid post ID: %r" % post_id
        )


def _serialize_post(
    ctx: rest.Context, post: Optional[model.Post]
) -> rest.Response:
    return posts.serialize_post(
        post, ctx.user, options=["thumbnailUrl", "user"]
    )


@rest.routes.get("/oembed/?")
def get_post(
    ctx: rest.Context, _params: Dict[str, str] = {}, url: str = ""
) -> rest.Response:
    #auth.verify_privilege(ctx.user, "posts:view")

    url = url or ctx.get_param_as_string("url")
    match = re.match(r".*?/(?P<post_id>\d+)", url)
    if not match:
        raise posts.InvalidPostIdError("Invalid post ID")

    host = ctx.get_header('X-Original-Host')
    home_url = f"https://{host}"
    site = config.config["sites"][host]

    post_id = _get_post_id(match)
    post = _get_post(post_id)
    serialized = _serialize_post(ctx, post)
    embed = {
        "version": "1.0",
        "type": "photo",
        "title": f"{site['name']} – #{post_id}",
        "author_name": serialized["user"]["name"] if serialized["user"] else None,
        "provider_name": site["name"],
        "provider_url": home_url,
        "thumbnail_url": f"{home_url}{serialized['thumbnailUrl']}",
        "thumbnail_width": int(config.config["thumbnails"]["post_width"]),
        "thumbnail_height": int(config.config["thumbnails"]["post_height"]),
        "url": f"{home_url}{serialized['thumbnailUrl']}",
        "width": int(config.config["thumbnails"]["post_width"]),
        "height": int(config.config["thumbnails"]["post_height"])
    }
    return embed


@rest.routes.get("/embed(?P<path>/.+)")
def post_index(ctx: rest.Context, params: Dict[str, str]) -> rest.Response:
    path = _index_path(params)
    try:
        oembed = get_post(ctx, {}, path)
    except posts.PostNotFoundError:
        return {"return_type": "custom", "status_code": "404", "content": index_html}

    host = ctx.get_header('X-Original-Host')
    home_url = f"https://{host}"
    site = config.config["sites"][host]
    url = home_url + path
    new_html = index_html.replace("</head>", f'''
<meta property="og:site_name" content="{site["name"]}">
<meta property="og:url" content="{html.escape(url)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(oembed['title'])}">
<meta name="twitter:title" content="{html.escape(oembed['title'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{html.escape(oembed['url'])}">
<meta property="og:image:url" content="{html.escape(oembed['url'])}">
<meta property="og:image:width" content="{oembed['width']}">
<meta property="og:image:height" content="{oembed['height']}">
<meta property="article:author" content="{html.escape(oembed['author_name'] or '')}">
<link rel="alternate" type="application/json+oembed" href="{home_url}/api/oembed?url={quote(html.escape(url))}" title="{html.escape(site["name"])}"></head>
''').replace("<html>", '<html prefix="og: http://ogp.me/ns#">').replace("<title>Loading...</title>", f"<title>{html.escape(oembed['title'])}</title>").replace("$THEME_COLOR$", site["color"]).replace("<!-- Base HTML Placeholder -->", f'<title>{site["name"]}</title><base id="base" href="/"/><meta name="description" content="{site.get("meta_description", "")}"/>')
    return {"return_type": "custom", "content": new_html}
