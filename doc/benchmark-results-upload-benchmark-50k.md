# Upload Benchmark (50k dataset, optimized)

Base URL: `http://localhost:4000/api`
Run time: `2026-01-23 17:07:24`

## Results

| Benchmark | p50 | p95 | p99 | avg | status |
|---|---:|---:|---:|---:|---|
| Upload (0 tags) | 0.0559 | 0.0566 | 0.0566 | 0.0555 | 200:5 |
| Upload (5 tags) | 0.0629 | 0.1623 | 0.1623 | 0.0827 | 200:5 |
| Upload (20 tags) | 0.0613 | 0.0635 | 0.0635 | 0.0617 | 200:5 |
| Update tags (0 -> 5) | 0.0135 | 0.0168 | 0.0168 | 0.0139 | 200:5 |
| Update tags (5 -> 20) | 0.0193 | 0.0358 | 0.0358 | 0.0222 | 200:5 |
| Update tags (20 -> 5) | 0.0212 | 0.0570 | 0.0570 | 0.0292 | 200:5 |
