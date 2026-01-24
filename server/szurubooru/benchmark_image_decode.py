"""Micro-benchmark image decode + grayscale conversion.

This mirrors the preprocessing path used by image signature generation:
decode bytes -> grayscale -> numpy array. Optional resize is supported
for future hashing pipelines.
"""

from __future__ import annotations

import argparse
import gc
import os
import platform
import random
import sys
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

# pillow-heif provides both HEIF and AVIF support
import pillow_heif

pillow_heif.register_heif_opener()  # Also registers AVIF opener
from PIL import Image as PILImage


@dataclass
class BenchResult:
    name: str
    count: int
    failures: int
    median_ms: float
    p95_ms: float
    avg_ms: float
    total_s: float


def _load_paths(paths: Sequence[str]) -> List[str]:
    out: List[str] = []
    for path in paths:
        if not path:
            continue
        if os.path.isdir(path):
            for entry in os.scandir(path):
                if entry.is_file():
                    out.append(entry.path)
        elif os.path.isfile(path):
            out.append(path)
    return out


def _read_files(paths: Sequence[str]) -> List[Tuple[str, bytes]]:
    samples: List[Tuple[str, bytes]] = []
    for path in paths:
        try:
            with open(path, "rb") as handle:
                samples.append((path, handle.read()))
        except OSError:
            continue
    return samples


def _filter_pillow_decodable(
    samples: Sequence[Tuple[str, bytes]],
) -> List[Tuple[str, bytes]]:
    filtered: List[Tuple[str, bytes]] = []
    for path, buf in samples:
        try:
            img = PILImage.open(BytesIO(buf))
            img.verify()
        except Exception:
            continue
        filtered.append((path, buf))
    return filtered


def _decode_pillow(buf: bytes, resize: Optional[int]) -> np.ndarray:
    img = PILImage.open(BytesIO(buf))
    if resize:
        img = img.resize((resize, resize), resample=PILImage.BILINEAR)
    return np.asarray(img.convert("L"), dtype=np.uint8)


def _decode_opencv(buf: bytes, resize: Optional[int]) -> np.ndarray:
    import cv2

    arr = np.frombuffer(buf, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("OpenCV decode failed")
    if resize:
        img = cv2.resize(img, (resize, resize), interpolation=cv2.INTER_AREA)
    return img


def _decode_pyvips(buf: bytes, resize: Optional[int]) -> np.ndarray:
    import pyvips

    img = pyvips.Image.new_from_buffer(buf, "", access="sequential")
    if resize:
        scale_x = resize / img.width
        scale_y = resize / img.height
        img = img.resize(scale_x, vscale=scale_y)
    if img.bands > 1:
        img = img.colourspace("b-w")
    mem = img.write_to_memory()
    arr = np.frombuffer(mem, dtype=np.uint8)
    return arr.reshape(img.height, img.width)


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = int(round((p / 100.0) * (len(values) - 1)))
    return values[idx]


def _bench(
    name: str,
    fn: Callable[[bytes, Optional[int]], np.ndarray],
    samples: Sequence[Tuple[str, bytes]],
    iterations: int,
    resize: Optional[int],
) -> BenchResult:
    # Warm-up
    for _, buf in samples[:5]:
        try:
            fn(buf, resize)
        except Exception:
            pass

    times: List[float] = []
    failures = 0
    start_all = time.perf_counter()
    for _ in range(iterations):
        for _, buf in samples:
            start = time.perf_counter()
            try:
                fn(buf, resize)
            except Exception:
                failures += 1
            times.append(time.perf_counter() - start)
    total_s = time.perf_counter() - start_all
    if times:
        median_ms = _percentile(times, 50) * 1000.0
        p95_ms = _percentile(times, 95) * 1000.0
        avg_ms = (sum(times) / len(times)) * 1000.0
    else:
        median_ms = p95_ms = avg_ms = 0.0
    return BenchResult(
        name=name,
        count=len(times),
        failures=failures,
        median_ms=median_ms,
        p95_ms=p95_ms,
        avg_ms=avg_ms,
        total_s=total_s,
    )


def _print_header(samples: Sequence[Tuple[str, bytes]], resize: Optional[int]) -> None:
    print("image decode micro-benchmark")
    print(f"python: {platform.python_version()} ({platform.platform()})")
    print(f"samples: {len(samples)}")
    print(f"resize: {resize if resize else 'none'}")
    try:
        import PIL

        print(f"Pillow: {PIL.__version__}")
    except Exception:
        print("Pillow: not available")
    for name in ["pyvips", "cv2"]:
        try:
            mod = __import__(name)
            print(f"{name}: {getattr(mod, '__version__', 'unknown')}")
        except Exception:
            print(f"{name}: not available")
    print("")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark decode+grayscale performance for hashing pipeline."
    )
    parser.add_argument(
        "--data-dir",
        default="/data/posts",
        help="Directory of post files (default: /data/posts)",
    )
    parser.add_argument(
        "--extra-dir",
        default="/opt/app/szurubooru/tests/assets",
        help="Extra directory of sample files",
    )
    parser.add_argument("--sample", type=int, default=500)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--resize", type=int, default=0)
    parser.add_argument("--seed", type=int, default=1337)
    args = parser.parse_args()

    paths = _load_paths([args.data_dir, args.extra_dir])
    if not paths:
        print("No input images found.")
        return 1
    rng = random.Random(args.seed)
    if len(paths) > args.sample:
        paths = rng.sample(paths, args.sample)

    samples = _read_files(paths)
    if not samples:
        print("Unable to read any sample images.")
        return 1
    samples = _filter_pillow_decodable(samples)
    if not samples:
        print("No Pillow-decodable samples found.")
        return 1

    resize = args.resize if args.resize > 0 else None
    _print_header(samples, resize)

    gc.disable()

    results: List[BenchResult] = []
    results.append(
        _bench("pillow", _decode_pillow, samples, args.iterations, resize)
    )

    try:
        import pyvips  # noqa: F401

        results.append(
            _bench("pyvips", _decode_pyvips, samples, args.iterations, resize)
        )
    except Exception:
        results.append(
            BenchResult(
                name="pyvips",
                count=0,
                failures=0,
                median_ms=0.0,
                p95_ms=0.0,
                avg_ms=0.0,
                total_s=0.0,
            )
        )

    try:
        import cv2  # noqa: F401

        results.append(
            _bench("opencv", _decode_opencv, samples, args.iterations, resize)
        )
    except Exception:
        results.append(
            BenchResult(
                name="opencv",
                count=0,
                failures=0,
                median_ms=0.0,
                p95_ms=0.0,
                avg_ms=0.0,
                total_s=0.0,
            )
        )

    print("results:")
    for res in results:
        if res.count == 0:
            print(f"  - {res.name}: not available")
            continue
        print(
            "  - {name}: n={count} fail={fail} median={median:.3f}ms "
            "p95={p95:.3f}ms avg={avg:.3f}ms total={total:.2f}s".format(
                name=res.name,
                count=res.count,
                fail=res.failures,
                median=res.median_ms,
                p95=res.p95_ms,
                avg=res.avg_ms,
                total=res.total_s,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
