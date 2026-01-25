"""Seed dev DB with near-duplicate image posts for testing."""

from __future__ import annotations

import argparse
import io
import os
import random
import sys
from typing import Iterable, List, Tuple

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from PIL import Image, ImageDraw, ImageEnhance

from szurubooru import config, db, model
from szurubooru.func import posts


def _render_base(seed: int, size: Tuple[int, int]) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", size, (30, 30, 30))
    draw = ImageDraw.Draw(img)

    for _ in range(6):
        x0 = rng.randint(0, size[0] // 2)
        y0 = rng.randint(0, size[1] // 2)
        x1 = rng.randint(x0 + 40, size[0])
        y1 = rng.randint(y0 + 40, size[1])
        color = tuple(rng.randint(60, 220) for _ in range(3))
        draw.rectangle([x0, y0, x1, y1], outline=color, fill=color)

    for _ in range(4):
        x0 = rng.randint(0, size[0] - 60)
        y0 = rng.randint(0, size[1] - 60)
        x1 = x0 + rng.randint(30, 120)
        y1 = y0 + rng.randint(30, 120)
        color = tuple(rng.randint(40, 200) for _ in range(3))
        draw.ellipse([x0, y0, x1, y1], outline=color, fill=color)

    return img


def _variant_resize(img: Image.Image, factor: float) -> Image.Image:
    width, height = img.size
    resized = img.resize(
        (int(width * factor), int(height * factor)), Image.LANCZOS
    )
    return resized.resize((width, height), Image.LANCZOS)


def _variant_crop(img: Image.Image, crop_px: int) -> Image.Image:
    width, height = img.size
    cropped = img.crop((crop_px, crop_px, width - crop_px, height - crop_px))
    return cropped.resize((width, height), Image.LANCZOS)


def _variant_brightness(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Brightness(img).enhance(factor)


def _to_jpeg_bytes(img: Image.Image, quality: int = 92) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def _create_post(content: bytes, tags: List[str]) -> model.Post:
    post, _new_tags = posts.create_post(content, tags, user=None)
    return post


def _seed_group(
    base_tags: List[str],
    variants: Iterable[Tuple[str, Image.Image]],
) -> List[model.Post]:
    created: List[model.Post] = []
    for tag, img in variants:
        tags = base_tags + [tag]
        created.append(_create_post(_to_jpeg_bytes(img), tags))
    return created


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed dev DB with near-duplicate image posts."
    )
    parser.add_argument("--groups", type=int, default=2)
    parser.add_argument("--size", type=str, default="640x480")
    parser.add_argument("--prefix", type=str, default="demo_dupe")
    args = parser.parse_args()

    if not config.config.get("dev"):
        raise SystemExit("This script is intended for dev config only.")

    if "x" not in args.size:
        raise SystemExit("--size must be like 640x480")
    width_str, height_str = args.size.split("x", 1)
    size = (int(width_str), int(height_str))

    created_posts: List[model.Post] = []

    for index in range(1, args.groups + 1):
        group_tag = f"{args.prefix}_{index}"
        base_tags = ["demo", "near_duplicate", group_tag]
        base = _render_base(1000 + index, size)
        variants = [
            ("variant_a", base),
            ("variant_b", _variant_resize(base, 0.92)),
            ("variant_c", _variant_crop(base, 12)),
            ("variant_d", _variant_brightness(base, 1.05)),
        ]
        created_posts.extend(_seed_group(base_tags, variants))

    unique = _render_base(9001, size)
    created_posts.append(
        _create_post(
            _to_jpeg_bytes(unique), ["demo", "unique_control", "solo"]
        )
    )

    db.session.commit()

    print("created posts:")
    for post in created_posts:
        tags = sorted(tag.first_name for tag in post.tags)
        print(f"  id={post.post_id} tags={','.join(tags)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
