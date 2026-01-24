# Upload/Tag Update Benchmark (post-implementation)

Base URL: `http://localhost:4000/api`
Run time: `2026-01-23 19:24:13`

## Results

| Benchmark | p50 | p95 | p99 | avg | status |
|---|---:|---:|---:|---:|---|
| Upload (0 tags) | 0.0633 | 0.0823 | 0.1214 | 0.0653 | 200:30 |
| Upload (5 tags) | 0.0574 | 0.0766 | 0.0966 | 0.0618 | 200:30 |
| Upload (20 tags) | 0.0779 | 0.0960 | 0.2207 | 0.0826 | 200:30 |
| Update tags (0 -> 5) | 0.0145 | 0.0250 | 0.0319 | 0.0159 | 200:30 |
| Update tags (5 -> 20) | 0.0234 | 0.0304 | 0.0674 | 0.0253 | 200:30 |
| Update tags (20 -> 5) | 0.0192 | 0.0334 | 0.0335 | 0.0221 | 200:30 |
