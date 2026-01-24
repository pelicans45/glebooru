# Post-Implementation Benchmark (50k posts, iter120, post view tuned)

Base URL: `http://localhost:4000/api`
Total posts (from API): `50099`
Run time: `2026-01-23 19:46:29`

## Sampled Post IDs

- No tags: 50003, 50002, 50001, 49990, 49987
- Few tags (1-3): 49995, 49994, 49993, 49976, 49973
- Many tags (>=12): 50069, 50068, 50067, 50066, 50065

## Benchmarks

### Gallery (default query)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0098, p95=0.0356, p99=0.0480, avg=0.0128
- Status counts: `200:120`

### Gallery (tag filter: tag_01725)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=tag_01725`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0175, p95=0.0359, p99=0.0992, avg=0.0210
- Status counts: `200:120`

### Gallery (sort:tag-count)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=sort%3Atag-count`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0162, p95=0.0299, p99=0.0460, avg=0.0176
- Status counts: `200:120`

### Gallery (large offset 20000)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=&offset=20000`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0113, p95=0.0272, p99=0.0481, avg=0.0132
- Status counts: `200:120`

### Post view (no tags) id=50003

- URL: `http://localhost:4000/api/post/50003?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0115, p95=0.0281, p99=0.0891, avg=0.0152
- Status counts: `200:120`

### Post view (no tags) id=50002

- URL: `http://localhost:4000/api/post/50002?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0118, p95=0.0228, p99=0.0259, avg=0.0130
- Status counts: `200:120`

### Post view (no tags) id=50001

- URL: `http://localhost:4000/api/post/50001?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0093, p95=0.0156, p99=0.0199, avg=0.0098
- Status counts: `200:120`

### Post view (no tags) id=49990

- URL: `http://localhost:4000/api/post/49990?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0128, p95=0.0225, p99=0.0354, avg=0.0137
- Status counts: `200:120`

### Post view (no tags) id=49987

- URL: `http://localhost:4000/api/post/49987?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0141, p95=0.0215, p99=0.0239, avg=0.0139
- Status counts: `200:120`

### Post view (few tags) id=49995

- URL: `http://localhost:4000/api/post/49995?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0134, p95=0.0208, p99=0.0236, avg=0.0137
- Status counts: `200:120`

### Post view (few tags) id=49994

- URL: `http://localhost:4000/api/post/49994?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0121, p95=0.0229, p99=0.0311, avg=0.0130
- Status counts: `200:120`

### Post view (few tags) id=49993

- URL: `http://localhost:4000/api/post/49993?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0133, p95=0.0204, p99=0.0269, avg=0.0133
- Status counts: `200:120`

### Post view (few tags) id=49976

- URL: `http://localhost:4000/api/post/49976?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0128, p95=0.0200, p99=0.0266, avg=0.0129
- Status counts: `200:120`

### Post view (few tags) id=49973

- URL: `http://localhost:4000/api/post/49973?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0118, p95=0.0183, p99=0.0225, avg=0.0121
- Status counts: `200:120`

### Post view (many tags) id=50069

- URL: `http://localhost:4000/api/post/50069?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0124, p95=0.0192, p99=0.0289, avg=0.0131
- Status counts: `200:120`

### Post view (many tags) id=50068

- URL: `http://localhost:4000/api/post/50068?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0122, p95=0.0301, p99=0.0373, avg=0.0141
- Status counts: `200:120`

### Post view (many tags) id=50067

- URL: `http://localhost:4000/api/post/50067?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0136, p95=0.0617, p99=0.1865, avg=0.0237
- Status counts: `200:120`

### Post view (many tags) id=50066

- URL: `http://localhost:4000/api/post/50066?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0147, p95=0.0316, p99=0.0677, avg=0.0170
- Status counts: `200:120`

### Post view (many tags) id=50065

- URL: `http://localhost:4000/api/post/50065?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0142, p95=0.0319, p99=0.0432, avg=0.0159
- Status counts: `200:120`
