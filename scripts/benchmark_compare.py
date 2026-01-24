#!/usr/bin/env python3
"""
Generate a Markdown comparison table for two benchmark reports.
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


def _delta(pre: float, post: float) -> str:
    if pre == 0:
        return "n/a"
    pct = (post - pre) / pre * 100.0
    return f"{pct:+.1f}%"


def _parse_write_report(path: Path) -> List[Dict[str, str]]:
    if not path or not path.exists():
        return []
    rows: List[Dict[str, str]] = []
    in_table = False
    for line in path.read_text().splitlines():
        if line.startswith("| Benchmark |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table:
            if not line.startswith("|"):
                break
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) < 6:
                continue
            rows.append(
                {
                    "name": parts[0],
                    "p50": parts[1],
                    "p95": parts[2],
                    "p99": parts[3],
                    "avg": parts[4],
                    "status": parts[5],
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare benchmark markdown files")
    parser.add_argument("--pre", required=True)
    parser.add_argument("--post", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="Benchmark Comparison")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    pre_path = Path(args.pre)
    post_path = Path(args.post)
    output_path = Path(args.output)

    order, pre_metrics = _parse_benchmarks(pre_path)
    _, post_metrics = _parse_benchmarks(post_path)

    lines: List[str] = []
    lines.append(f"# {args.title}")
    lines.append("")
    lines.append(f"Baseline: {args.pre}")
    lines.append(f"Post-implementation (iter=120): {args.post}")
    if args.write_report:
        lines.append(f"Write benchmark: {args.write_report}")
    lines.append("")
    lines.append("## Read benchmarks (pre vs post)")
    lines.append("")
    lines.append(
        "| Benchmark | p50 pre | p50 post | Δp50 | p95 pre | p95 post | Δp95 | avg pre | avg post | Δavg |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for name in order:
        if name not in pre_metrics or name not in post_metrics:
            continue
        pre = pre_metrics[name]
        post = post_metrics[name]
        lines.append(
            "| "
            + name
            + f" | {pre['p50']:.4f} | {post['p50']:.4f} | {_delta(pre['p50'], post['p50'])}"
            + f" | {pre['p95']:.4f} | {post['p95']:.4f} | {_delta(pre['p95'], post['p95'])}"
            + f" | {pre['avg']:.4f} | {post['avg']:.4f} | {_delta(pre['avg'], post['avg'])} |"
        )

    if args.write_report:
        write_rows = _parse_write_report(Path(args.write_report))
        if write_rows:
            lines.append("")
            lines.append("## Write benchmarks (post only)")
            lines.append("")
            lines.append("| Benchmark | p50 | p95 | p99 | avg | status |")
            lines.append("|---|---:|---:|---:|---:|---|")
            for row in write_rows:
                lines.append(
                    "| "
                    + row["name"]
                    + f" | {row['p50']} | {row['p95']} | {row['p99']} | {row['avg']} | {row['status']} |"
                )

    output_path.write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
