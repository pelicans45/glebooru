from datetime import datetime
from typing import Dict
from xml.sax.saxutils import escape

from szurubooru import db, model, rest


def _format_date(dt: datetime) -> str:
    """Format datetime as W3C datetime format for sitemaps."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


@rest.routes.get("/sitemap\\.xml")
def get_sitemap(ctx: rest.Context, _params: Dict[str, str] = {}) -> rest.Response:
    """Generate XML sitemap for search engines."""
    host = ctx.get_header("Host")
    if not host:
        host = "example.com"

    base_url = f"https://{host}"

    # Start XML
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # Add homepage
    xml_parts.append(f"""  <url>
    <loc>{escape(base_url)}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

    # Add posts page
    xml_parts.append(f"""  <url>
    <loc>{escape(base_url)}/posts</loc>
    <changefreq>hourly</changefreq>
    <priority>0.9</priority>
  </url>""")

    # Add tags page
    xml_parts.append(f"""  <url>
    <loc>{escape(base_url)}/tags</loc>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>""")

    # Add pools page
    xml_parts.append(f"""  <url>
    <loc>{escape(base_url)}/pools</loc>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>""")

    # Add individual posts (limit to recent/popular posts for performance)
    posts = (
        db.session()
        .query(model.Post.post_id, model.Post.last_edit_time, model.Post.creation_time)
        .order_by(model.Post.post_id.desc())
        .limit(1000)
        .all()
    )

    for post in posts:
        post_id, last_edit, creation = post
        last_mod = last_edit or creation
        xml_parts.append(f"""  <url>
    <loc>{escape(base_url)}/post/{post_id}</loc>
    <lastmod>{_format_date(last_mod)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>""")

    xml_parts.append("</urlset>")

    return {
        "return_type": "custom",
        "content_type": "application/xml",
        "content": "\n".join(xml_parts),
    }
