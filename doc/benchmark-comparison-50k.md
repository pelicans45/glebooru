# Benchmark Comparison (50k posts)

Baseline: doc/benchmark-results-pre-implementation-50k.md
Post-implementation (optimized writes): doc/benchmark-results-post-implementation-50k-optimized.md
Write benchmark: doc/benchmark-results-upload-benchmark-50k.md

## Read benchmarks (pre vs post)

| Benchmark | p50 pre | p50 post | Δp50 | p95 pre | p95 post | Δp95 | avg pre | avg post | Δavg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Gallery (default query) | 0.0258 | 0.0090 | -65.1% | 0.0523 | 0.0766 | +46.5% | 0.0304 | 0.0164 | -46.1% |
| Gallery (tag filter: tag_01760) | 0.0300 | 0.0169 | -43.7% | 0.0405 | 0.0307 | -24.2% | 0.0318 | 0.0182 | -42.8% |
| Gallery (sort:tag-count) | 0.0363 | 0.0225 | -38.0% | 0.4592 | 0.1348 | -70.6% | 0.0977 | 0.0391 | -60.0% |
| Gallery (large offset 20000) | 0.0232 | 0.0102 | -56.0% | 0.0305 | 0.0802 | +163.0% | 0.0241 | 0.0196 | -18.7% |
| Post view (no tags) id=49990 | 0.0117 | 0.0103 | -12.0% | 0.0167 | 0.0152 | -9.0% | 0.0118 | 0.0106 | -10.2% |
| Post view (no tags) id=49987 | 0.0129 | 0.0155 | +20.2% | 0.0179 | 0.0221 | +23.5% | 0.0127 | 0.0156 | +22.8% |
| Post view (no tags) id=49975 | 0.0131 | 0.0115 | -12.2% | 0.0178 | 0.0155 | -12.9% | 0.0126 | 0.0113 | -10.3% |
| Post view (no tags) id=49970 | 0.0116 | 0.0090 | -22.4% | 0.0165 | 0.0150 | -9.1% | 0.0117 | 0.0094 | -19.7% |
| Post view (no tags) id=49967 | 0.0110 | 0.0085 | -22.7% | 0.0222 | 0.0140 | -36.9% | 0.0123 | 0.0092 | -25.2% |
| Post view (few tags) id=49995 | 0.0097 | 0.0111 | +14.4% | 0.0153 | 0.0183 | +19.6% | 0.0104 | 0.0117 | +12.5% |
| Post view (few tags) id=49994 | 0.0151 | 0.0107 | -29.1% | 0.0221 | 0.0175 | -20.8% | 0.0145 | 0.0111 | -23.4% |
| Post view (few tags) id=49993 | 0.0131 | 0.0115 | -12.2% | 0.0188 | 0.0148 | -21.3% | 0.0135 | 0.0112 | -17.0% |
| Post view (few tags) id=49976 | 0.0108 | 0.0097 | -10.2% | 0.0166 | 0.0167 | +0.6% | 0.0115 | 0.0108 | -6.1% |
| Post view (few tags) id=49973 | 0.0118 | 0.0121 | +2.5% | 0.0163 | 0.0198 | +21.5% | 0.0115 | 0.0116 | +0.9% |
| Post view (many tags) id=50000 | 0.0149 | 0.0130 | -12.8% | 0.0208 | 0.0232 | +11.5% | 0.0159 | 0.0138 | -13.2% |
| Post view (many tags) id=49998 | 0.0147 | 0.0127 | -13.6% | 0.0395 | 0.0189 | -52.2% | 0.0197 | 0.0127 | -35.5% |
| Post view (many tags) id=49997 | 0.0278 | 0.0131 | -52.9% | 0.1064 | 0.0197 | -81.5% | 0.0375 | 0.0133 | -64.5% |
| Post view (many tags) id=49992 | 0.0289 | 0.0130 | -55.0% | 0.0822 | 0.0197 | -76.0% | 0.0396 | 0.0136 | -65.7% |
| Post view (many tags) id=49988 | 0.0185 | 0.0135 | -27.0% | 0.0265 | 0.0273 | +3.0% | 0.0182 | 0.0137 | -24.7% |

## Write benchmarks (post only)

No pre-implementation write benchmark was captured for these exact scenarios.

| Benchmark | p50 post | p95 post | p99 post | avg post |
|---|---:|---:|---:|---:|
| Upload (0 tags) | 0.0559 | 0.0566 | 0.0566 | 0.0555 |
| Upload (5 tags) | 0.0629 | 0.1623 | 0.1623 | 0.0827 |
| Upload (20 tags) | 0.0613 | 0.0635 | 0.0635 | 0.0617 |
| Update tags (0 -> 5) | 0.0135 | 0.0168 | 0.0168 | 0.0139 |
| Update tags (5 -> 20) | 0.0193 | 0.0358 | 0.0358 | 0.0222 |
| Update tags (20 -> 5) | 0.0212 | 0.0570 | 0.0570 | 0.0292 |
