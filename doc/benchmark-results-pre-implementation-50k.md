# Pre-Implementation Benchmark (50k posts)

Base URL: `http://localhost:4000/api`
Total posts (from API): `50000`
Run time: `2026-01-23 00:59:24`

## Sampled Post IDs

- No tags: 49990, 49987, 49975, 49970, 49967
- Few tags (1-3): 49995, 49994, 49993, 49976, 49973
- Many tags (>=12): 50000, 49998, 49997, 49992, 49988

## Benchmarks

### Gallery (default query)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0258, p95=0.0523, p99=0.0642, avg=0.0304
- Status counts: `200:30`

### Gallery (tag filter: tag_01760)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=tag_01760`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0300, p95=0.0405, p99=0.0501, avg=0.0318
- Status counts: `200:30`

### Gallery (sort:tag-count)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=sort%3Atag-count`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0363, p95=0.4592, p99=0.5066, avg=0.0977
- Status counts: `200:30`

### Gallery (large offset 20000)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=&offset=20000`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0232, p95=0.0305, p99=0.0535, avg=0.0241
- Status counts: `200:30`

### Post view (no tags) id=49990

- URL: `http://localhost:4000/api/post/49990?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0117, p95=0.0167, p99=0.0223, avg=0.0118
- Status counts: `200:30`

### Post view (no tags) id=49987

- URL: `http://localhost:4000/api/post/49987?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0129, p95=0.0179, p99=0.0253, avg=0.0127
- Status counts: `200:30`

### Post view (no tags) id=49975

- URL: `http://localhost:4000/api/post/49975?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0131, p95=0.0178, p99=0.0209, avg=0.0126
- Status counts: `200:30`

### Post view (no tags) id=49970

- URL: `http://localhost:4000/api/post/49970?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0116, p95=0.0165, p99=0.0228, avg=0.0117
- Status counts: `200:30`

### Post view (no tags) id=49967

- URL: `http://localhost:4000/api/post/49967?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0110, p95=0.0222, p99=0.0228, avg=0.0123
- Status counts: `200:30`

### Post view (few tags) id=49995

- URL: `http://localhost:4000/api/post/49995?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0097, p95=0.0153, p99=0.0156, avg=0.0104
- Status counts: `200:30`

### Post view (few tags) id=49994

- URL: `http://localhost:4000/api/post/49994?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0151, p95=0.0221, p99=0.0265, avg=0.0145
- Status counts: `200:30`

### Post view (few tags) id=49993

- URL: `http://localhost:4000/api/post/49993?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0131, p95=0.0188, p99=0.0272, avg=0.0135
- Status counts: `200:30`

### Post view (few tags) id=49976

- URL: `http://localhost:4000/api/post/49976?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0108, p95=0.0166, p99=0.0244, avg=0.0115
- Status counts: `200:30`

### Post view (few tags) id=49973

- URL: `http://localhost:4000/api/post/49973?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0118, p95=0.0163, p99=0.0193, avg=0.0115
- Status counts: `200:30`

### Post view (many tags) id=50000

- URL: `http://localhost:4000/api/post/50000?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0149, p95=0.0208, p99=0.0287, avg=0.0159
- Status counts: `200:30`

### Post view (many tags) id=49998

- URL: `http://localhost:4000/api/post/49998?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0147, p95=0.0395, p99=0.0407, avg=0.0197
- Status counts: `200:30`

### Post view (many tags) id=49997

- URL: `http://localhost:4000/api/post/49997?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0278, p95=0.1064, p99=0.1133, avg=0.0375
- Status counts: `200:30`

### Post view (many tags) id=49992

- URL: `http://localhost:4000/api/post/49992?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0289, p95=0.0822, p99=0.1052, avg=0.0396
- Status counts: `200:30`

### Post view (many tags) id=49988

- URL: `http://localhost:4000/api/post/49988?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0185, p95=0.0265, p99=0.0319, avg=0.0182
- Status counts: `200:30`
