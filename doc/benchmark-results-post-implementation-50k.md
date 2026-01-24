# Post-Implementation Benchmark (50k posts)

Base URL: `http://localhost:4000/api`
Total posts (from API): `50000`
Run time: `2026-01-23 14:32:14`

## Sampled Post IDs

- No tags: 49990, 49987, 49975, 49970, 49967
- Few tags (1-3): 49995, 49994, 49993, 49976, 49973
- Many tags (>=12): 50000, 49998, 49997, 49992, 49988

## Benchmarks

### Gallery (default query)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0131, p95=0.0326, p99=0.0358, avg=0.0148
- Status counts: `200:30`

### Gallery (tag filter: tag_01760)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=tag_01760`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0154, p95=0.0653, p99=0.0674, avg=0.0193
- Status counts: `200:30`

### Gallery (sort:tag-count)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=sort%3Atag-count`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0171, p95=0.1161, p99=0.1611, avg=0.0300
- Status counts: `200:30`

### Gallery (large offset 20000)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=&offset=20000`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0152, p95=0.1066, p99=0.1088, avg=0.0289
- Status counts: `200:30`

### Post view (no tags) id=49990

- URL: `http://localhost:4000/api/post/49990?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0148, p95=0.0199, p99=0.0206, avg=0.0143
- Status counts: `200:30`

### Post view (no tags) id=49987

- URL: `http://localhost:4000/api/post/49987?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0111, p95=0.0200, p99=0.0210, avg=0.0112
- Status counts: `200:30`

### Post view (no tags) id=49975

- URL: `http://localhost:4000/api/post/49975?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0103, p95=0.0182, p99=0.0188, avg=0.0113
- Status counts: `200:30`

### Post view (no tags) id=49970

- URL: `http://localhost:4000/api/post/49970?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0093, p95=0.0140, p99=0.0214, avg=0.0097
- Status counts: `200:30`

### Post view (no tags) id=49967

- URL: `http://localhost:4000/api/post/49967?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0113, p95=0.0241, p99=0.0415, avg=0.0144
- Status counts: `200:30`

### Post view (few tags) id=49995

- URL: `http://localhost:4000/api/post/49995?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0118, p95=0.0174, p99=0.0234, avg=0.0120
- Status counts: `200:30`

### Post view (few tags) id=49994

- URL: `http://localhost:4000/api/post/49994?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0108, p95=0.0156, p99=0.0236, avg=0.0112
- Status counts: `200:30`

### Post view (few tags) id=49993

- URL: `http://localhost:4000/api/post/49993?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0116, p95=0.0157, p99=0.0229, avg=0.0116
- Status counts: `200:30`

### Post view (few tags) id=49976

- URL: `http://localhost:4000/api/post/49976?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0109, p95=0.0160, p99=0.0204, avg=0.0111
- Status counts: `200:30`

### Post view (few tags) id=49973

- URL: `http://localhost:4000/api/post/49973?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0129, p95=0.0235, p99=0.0364, avg=0.0136
- Status counts: `200:30`

### Post view (many tags) id=50000

- URL: `http://localhost:4000/api/post/50000?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0119, p95=0.0171, p99=0.0236, avg=0.0124
- Status counts: `200:30`

### Post view (many tags) id=49998

- URL: `http://localhost:4000/api/post/49998?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0106, p95=0.0166, p99=0.0223, avg=0.0114
- Status counts: `200:30`

### Post view (many tags) id=49997

- URL: `http://localhost:4000/api/post/49997?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0119, p95=0.0187, p99=0.0204, avg=0.0121
- Status counts: `200:30`

### Post view (many tags) id=49992

- URL: `http://localhost:4000/api/post/49992?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0099, p95=0.0170, p99=0.0232, avg=0.0109
- Status counts: `200:30`

### Post view (many tags) id=49988

- URL: `http://localhost:4000/api/post/49988?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `30`
- Concurrency: `5`
- Latency (seconds): p50=0.0122, p95=0.0201, p99=0.0261, avg=0.0128
- Status counts: `200:30`
