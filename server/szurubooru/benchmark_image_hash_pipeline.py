"""Benchmark image hash generation pipeline (decode + signature + pack/words)."""

from __future__ import annotations

import argparse
import os
import platform
import random
import statistics
import time
import sys
from typing import List, Sequence, Tuple


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


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = int(round((p / 100.0) * (len(values) - 1)))
    return values[idx]


def _print_header(sample_count: int, iterations: int) -> None:
    print("image hash pipeline benchmark")
    print(f"python: {platform.python_version()} ({platform.platform()})")
    print(f"samples: {sample_count}")
    print(f"iterations: {iterations}")
    print(f"backend: {os.getenv('SZURUBOORU_IMAGE_HASH_BACKEND', 'default')}")
    print("")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark image signature generation pipeline."
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
    parser.add_argument("--sample", type=int, default=300)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--seed", type=int, default=1337)
    args = parser.parse_args()

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

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

    _print_header(len(samples), args.iterations)

    # Import after env var is set in caller.
    from szurubooru.func import image_hash  # pylint: disable=import-outside-toplevel

    # Filter samples to ones that can generate a signature.
    filtered: List[Tuple[str, bytes]] = []
    for path, buf in samples:
        try:
            image_hash.generate_signature(buf)
        except Exception:
            continue
        filtered.append((path, buf))

    if not filtered:
        print("No samples could generate a signature.")
        return 1

    times: List[float] = []
    failures = 0
    start_all = time.perf_counter()
    for _ in range(args.iterations):
        for _, buf in filtered:
            start = time.perf_counter()
            try:
                signature = image_hash.generate_signature(buf)
                image_hash.pack_signature(signature)
                image_hash.generate_words(signature)
            except Exception:
                failures += 1
            times.append(time.perf_counter() - start)
    total_s = time.perf_counter() - start_all

    median_ms = _percentile(times, 50) * 1000.0
    p95_ms = _percentile(times, 95) * 1000.0
    avg_ms = statistics.mean(times) * 1000.0 if times else 0.0

    print(
        "results: n={count} fail={fail} median={median:.3f}ms "
        "p95={p95:.3f}ms avg={avg:.3f}ms total={total:.2f}s".format(
            count=len(times),
            fail=failures,
            median=median_ms,
            p95=p95_ms,
            avg=avg_ms,
            total=total_s,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
