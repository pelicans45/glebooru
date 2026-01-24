# Post-Implementation Benchmark (50k posts, seed 1337)

Base URL: `http://localhost:4000/api`
Total posts (from API): `50000`
Run time: `2026-01-23 19:22:15`

## Sampled Post IDs

- No tags: 49990, 49987, 49975, 49970, 49967
- Few tags (1-3): 49995, 49994, 49993, 49976, 49973
- Many tags (>=12): 50000, 49998, 49997, 49992, 49988

## Benchmarks

### Gallery (default query)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0110, p95=0.0260, p99=0.0606, avg=0.0129
- Status counts: `200:120`

### Gallery (tag filter: tag_01760)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=tag_01760`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0136, p95=0.0250, p99=0.0283, avg=0.0146
- Status counts: `200:120`

### Gallery (sort:tag-count)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=sort%3Atag-count`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0267, p95=0.0590, p99=0.0733, avg=0.0294
- Status counts: `200:120`

### Gallery (large offset 20000)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=&offset=20000`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0127, p95=0.0245, p99=0.0767, avg=0.0151
- Status counts: `200:120`

### Post view (no tags) id=49990

- URL: `http://localhost:4000/api/post/49990?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0136, p95=0.0214, p99=0.0323, avg=0.0142
- Status counts: `200:120`

### Post view (no tags) id=49987

- URL: `http://localhost:4000/api/post/49987?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0138, p95=0.0283, p99=0.0335, avg=0.0150
- Status counts: `200:120`

### Post view (no tags) id=49975

- URL: `http://localhost:4000/api/post/49975?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0123, p95=0.0233, p99=0.0340, avg=0.0131
- Status counts: `200:120`

### Post view (no tags) id=49970

- URL: `http://localhost:4000/api/post/49970?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0132, p95=0.0226, p99=0.0257, avg=0.0132
- Status counts: `200:120`

### Post view (no tags) id=49967

- URL: `http://localhost:4000/api/post/49967?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0115, p95=0.0163, p99=0.0196, avg=0.0110
- Status counts: `200:120`

### Post view (few tags) id=49995

- URL: `http://localhost:4000/api/post/49995?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0137, p95=0.0367, p99=0.0505, avg=0.0156
- Status counts: `200:120`

### Post view (few tags) id=49994

- URL: `http://localhost:4000/api/post/49994?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0173, p95=0.0363, p99=0.0476, avg=0.0193
- Status counts: `200:120`

### Post view (few tags) id=49993

- URL: `http://localhost:4000/api/post/49993?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0159, p95=0.0268, p99=0.0338, avg=0.0165
- Status counts: `200:120`

### Post view (few tags) id=49976

- URL: `http://localhost:4000/api/post/49976?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0130, p95=0.0204, p99=0.0291, avg=0.0130
- Status counts: `200:120`

### Post view (few tags) id=49973

- URL: `http://localhost:4000/api/post/49973?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0134, p95=0.0233, p99=0.0413, avg=0.0142
- Status counts: `200:120`

### Post view (many tags) id=50000

- URL: `http://localhost:4000/api/post/50000?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0147, p95=0.0193, p99=0.0308, avg=0.0141
- Status counts: `200:120`

### Post view (many tags) id=49998

- URL: `http://localhost:4000/api/post/49998?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0150, p95=0.0227, p99=0.0345, avg=0.0146
- Status counts: `200:120`

### Post view (many tags) id=49997

- URL: `http://localhost:4000/api/post/49997?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0146, p95=0.0245, p99=0.0282, avg=0.0143
- Status counts: `200:120`

### Post view (many tags) id=49992

- URL: `http://localhost:4000/api/post/49992?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0142, p95=0.0222, p99=0.0248, avg=0.0143
- Status counts: `200:120`

### Post view (many tags) id=49988

- URL: `http://localhost:4000/api/post/49988?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0144, p95=0.0349, p99=0.0439, avg=0.0162
- Status counts: `200:120`
