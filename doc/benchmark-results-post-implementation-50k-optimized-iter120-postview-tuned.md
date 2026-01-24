# Post-Implementation Benchmark (50k posts, iter120, post view tuned)

Base URL: `http://localhost:4000/api`
Total posts (from API): `50000`
Run time: `2026-01-23 19:50:04`

## Sampled Post IDs

- No tags: 49990, 49987, 49975, 49970, 49967
- Few tags (1-3): 49995, 49994, 49993, 49976, 49973
- Many tags (>=12): 50000, 49998, 49997, 49992, 49988

## Benchmarks

### Gallery (default query)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0111, p95=0.0309, p99=0.0366, avg=0.0126
- Status counts: `200:120`

### Gallery (tag filter: tag_01760)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=tag_01760`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0155, p95=0.0351, p99=0.0819, avg=0.0180
- Status counts: `200:120`

### Gallery (sort:tag-count)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=sort%3Atag-count`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0224, p95=0.0464, p99=0.0593, avg=0.0250
- Status counts: `200:120`

### Gallery (large offset 20000)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=&offset=20000`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0129, p95=0.0290, p99=0.0367, avg=0.0145
- Status counts: `200:120`

### Post view (no tags) id=49990

- URL: `http://localhost:4000/api/post/49990?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0072, p95=0.0130, p99=0.0194, avg=0.0079
- Status counts: `200:120`

### Post view (no tags) id=49987

- URL: `http://localhost:4000/api/post/49987?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0078, p95=0.0124, p99=0.0196, avg=0.0082
- Status counts: `200:120`

### Post view (no tags) id=49975

- URL: `http://localhost:4000/api/post/49975?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0108, p95=0.0183, p99=0.0266, avg=0.0118
- Status counts: `200:120`

### Post view (no tags) id=49970

- URL: `http://localhost:4000/api/post/49970?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0097, p95=0.0180, p99=0.0212, avg=0.0104
- Status counts: `200:120`

### Post view (no tags) id=49967

- URL: `http://localhost:4000/api/post/49967?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0099, p95=0.0149, p99=0.0215, avg=0.0099
- Status counts: `200:120`

### Post view (few tags) id=49995

- URL: `http://localhost:4000/api/post/49995?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0106, p95=0.0176, p99=0.0278, avg=0.0110
- Status counts: `200:120`

### Post view (few tags) id=49994

- URL: `http://localhost:4000/api/post/49994?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0093, p95=0.0140, p99=0.0196, avg=0.0095
- Status counts: `200:120`

### Post view (few tags) id=49993

- URL: `http://localhost:4000/api/post/49993?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0094, p95=0.0153, p99=0.0184, avg=0.0099
- Status counts: `200:120`

### Post view (few tags) id=49976

- URL: `http://localhost:4000/api/post/49976?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0152, p95=0.0264, p99=0.0338, avg=0.0161
- Status counts: `200:120`

### Post view (few tags) id=49973

- URL: `http://localhost:4000/api/post/49973?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0119, p95=0.0298, p99=0.0727, avg=0.0159
- Status counts: `200:120`

### Post view (many tags) id=50000

- URL: `http://localhost:4000/api/post/50000?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0138, p95=0.0242, p99=0.0337, avg=0.0146
- Status counts: `200:120`

### Post view (many tags) id=49998

- URL: `http://localhost:4000/api/post/49998?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0124, p95=0.0314, p99=0.1471, avg=0.0185
- Status counts: `200:120`

### Post view (many tags) id=49997

- URL: `http://localhost:4000/api/post/49997?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0094, p95=0.0171, p99=0.0239, avg=0.0105
- Status counts: `200:120`

### Post view (many tags) id=49992

- URL: `http://localhost:4000/api/post/49992?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0082, p95=0.0130, p99=0.0167, avg=0.0085
- Status counts: `200:120`

### Post view (many tags) id=49988

- URL: `http://localhost:4000/api/post/49988?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0093, p95=0.0210, p99=0.0330, avg=0.0104
- Status counts: `200:120`
