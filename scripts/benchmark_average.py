#!/usr/bin/env python3
"""
Average multiple benchmark markdown reports into a single report.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

LATENCY_RE = re.compile(
    r"p50=([0-9.]+), p95=([0-9.]+), p99=([0-9.]+), avg=([0-9.]+)"
)


def _parse_benchmarks(path: Path) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
    order: List[str] = []
    metrics: Dict[str, Dict[str, float]] = {}
    current: str | None = None
    for line in path.read_text().splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            if current not in order:
                order.append(current)
            continue
        if current and line.startswith("- Latency"):
            match = LATENCY_RE.search(line)
            if not match:
                continue
            metrics[current] = {
                "p50": float(match.group(1)),
                "p95": float(match.group(2)),
                "p99": float(match.group(3)),
                "avg": float(match.group(4)),
            }
    return order, metrics


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def main() -> int:
    parser = argparse.ArgumentParser(description="Average benchmark reports")
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="Benchmark Average")
    parser.add_argument("inputs", nargs="+")
    args = parser.parse_args()

    input_paths = [Path(path) for path in args.inputs]
    parsed = [_parse_benchmarks(path) for path in input_paths]
    order = parsed[0][0]

    averages: Dict[str, Dict[str, float]] = {}
    for name in order:
        buckets: Dict[str, List[float]] = {
            "p50": [],
            "p95": [],
            "p99": [],
            "avg": [],
        }
        for _, metrics in parsed:
            if name not in metrics:
                continue
            for key in buckets:
                buckets[key].append(metrics[name][key])
        if not buckets["p50"]:
            continue
        averages[name] = {
            key: _mean(values) for key, values in buckets.items()
        }

    lines: List[str] = []
    lines.append(f"# {args.title}")
    lines.append("")
    lines.append("Inputs:")
    for path in input_paths:
        lines.append(f"- {path}")
    lines.append("")
    lines.append("## Benchmarks (averaged)")
    lines.append("")

    for name in order:
        if name not in averages:
            continue
        metrics = averages[name]
        lines.append(f"### {name}")
        lines.append("")
        lines.append(
            "- Latency (seconds): "
            f"p50={metrics['p50']:.4f}, "
            f"p95={metrics['p95']:.4f}, "
            f"p99={metrics['p99']:.4f}, "
            f"avg={metrics['avg']:.4f}"
        )
        lines.append("")

    Path(args.output).write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
