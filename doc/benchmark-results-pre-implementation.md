# API Benchmark Results (Pre-Implementation)

Base URL: `http://localhost:4000/api`
Total posts (from API): `20002`
Run time: `2026-01-22 23:40:08`

## Sampled Post IDs

- No tags: 20001
- Few tags (1-3): 20000, 19999, 19998, 19997, 19996
- Many tags (>=12): 20002

## Benchmarks

### Gallery (default query)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0119, p95=0.0816, p99=0.0848, avg=0.0208
- Status counts: `200:30`

### Gallery (tag filter: bench_tag_047)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=bench_tag_047`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0099, p95=0.0525, p99=0.0562, avg=0.0148
- Status counts: `200:30`

### Gallery (sort:tag-count)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=sort%3Atag-count`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0096, p95=0.0144, p99=0.0144, avg=0.0101
- Status counts: `200:30`

### Gallery (large offset 19952)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=&offset=19952`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0066, p95=0.1221, p99=0.1240, avg=0.0244
- Status counts: `200:30`

### Post view (no tags) id=20001

- URL: `http://localhost:4000/api/post/20001?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0113, p95=0.0241, p99=0.0254, avg=0.0118
- Status counts: `200:30`

### Post view (few tags) id=20000

- URL: `http://localhost:4000/api/post/20000?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0116, p95=0.0184, p99=0.0187, avg=0.0121
- Status counts: `200:30`

### Post view (few tags) id=19999

- URL: `http://localhost:4000/api/post/19999?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0101, p95=0.0175, p99=0.0182, avg=0.0110
- Status counts: `200:30`

### Post view (few tags) id=19998

- URL: `http://localhost:4000/api/post/19998?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0130, p95=0.0241, p99=0.0317, avg=0.0144
- Status counts: `200:30`

### Post view (few tags) id=19997

- URL: `http://localhost:4000/api/post/19997?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0217, p95=0.1117, p99=0.1682, avg=0.0429
- Status counts: `200:30`

### Post view (few tags) id=19996

- URL: `http://localhost:4000/api/post/19996?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0210, p95=0.0439, p99=0.0915, avg=0.0239
- Status counts: `200:30`

### Post view (many tags) id=20002

- URL: `http://localhost:4000/api/post/20002?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0232, p95=0.0318, p99=0.0373, avg=0.0237
- Status counts: `200:30`
