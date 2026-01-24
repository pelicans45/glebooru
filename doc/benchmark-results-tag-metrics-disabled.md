# API Benchmark Results (Tag Metrics Disabled)

Base URL: `http://localhost:4000/api`
Total posts (from API): `20002`
Run time: `2026-01-23 00:03:56`

## Sampled Post IDs

- No tags: 20001
- Few tags (1-3): 20000, 19999, 19998, 19997, 19996
- Many tags (>=12): 20002

## Benchmarks

### Gallery (default query)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0121, p95=0.0338, p99=0.0386, avg=0.0161
- Status counts: `200:30`

### Gallery (tag filter: bench_tag_047)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=bench_tag_047`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0122, p95=0.0608, p99=0.0903, avg=0.0201
- Status counts: `200:30`

### Gallery (sort:tag-count)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=sort%3Atag-count`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0150, p95=0.2236, p99=0.2299, avg=0.0472
- Status counts: `200:30`

### Gallery (large offset 19952)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=&offset=19952`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0063, p95=0.0125, p99=0.0218, avg=0.0070
- Status counts: `200:30`

### Post view (no tags) id=20001

- URL: `http://localhost:4000/api/post/20001?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0110, p95=0.0208, p99=0.0290, avg=0.0116
- Status counts: `200:30`

### Post view (few tags) id=20000

- URL: `http://localhost:4000/api/post/20000?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0122, p95=0.0241, p99=0.0289, avg=0.0131
- Status counts: `200:30`

### Post view (few tags) id=19999

- URL: `http://localhost:4000/api/post/19999?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0117, p95=0.0190, p99=0.0373, avg=0.0132
- Status counts: `200:30`

### Post view (few tags) id=19998

- URL: `http://localhost:4000/api/post/19998?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0121, p95=0.0160, p99=0.0250, avg=0.0121
- Status counts: `200:30`

### Post view (few tags) id=19997

- URL: `http://localhost:4000/api/post/19997?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0137, p95=0.0281, p99=0.0377, avg=0.0149
- Status counts: `200:30`

### Post view (few tags) id=19996

- URL: `http://localhost:4000/api/post/19996?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0128, p95=0.0193, p99=0.0242, avg=0.0132
- Status counts: `200:30`

### Post view (many tags) id=20002

- URL: `http://localhost:4000/api/post/20002?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0183, p95=0.0234, p99=0.0335, avg=0.0182
- Status counts: `200:30`
