# Post-Implementation Benchmark (50k posts, iter120, post view tuned)

Base URL: `http://localhost:4000/api`
Total posts (from API): `50000`
Run time: `2026-01-23 21:25:38`

## Sampled Post IDs

- No tags: 49990, 49987, 49975, 49970, 49967
- Few tags (1-3): 49995, 49994, 49993, 49976, 49973
- Many tags (>=12): 50000, 49998, 49997, 49992, 49988

## Benchmarks

### Gallery (default query)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0051, p95=0.0146, p99=0.0380, avg=0.0068
- Status counts: `200:120`

### Gallery (tag filter: tag_01760)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=tag_01760`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0081, p95=0.0494, p99=0.2456, avg=0.0188
- Status counts: `200:120`

### Gallery (sort:tag-count)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=sort%3Atag-count`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0079, p95=0.0352, p99=0.1922, avg=0.0169
- Status counts: `200:120`

### Gallery (large offset 20000)

- URL: `http://localhost:4000/api/posts?limit=42&fields=id%2CthumbnailUrl%2CcontentUrl%2CcreationTime%2Ctype%2Csafety%2Cscore%2CfavoriteCount%2CcommentCount%2CtagsBasic%2Cversion&query=&offset=20000`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0061, p95=0.0159, p99=0.0245, avg=0.0072
- Status counts: `200:120`

### Post view (no tags) id=49990

- URL: `http://localhost:4000/api/post/49990?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0062, p95=0.0117, p99=0.0201, avg=0.0069
- Status counts: `200:120`

### Post view (no tags) id=49987

- URL: `http://localhost:4000/api/post/49987?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0057, p95=0.0096, p99=0.0141, avg=0.0060
- Status counts: `200:120`

### Post view (no tags) id=49975

- URL: `http://localhost:4000/api/post/49975?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0072, p95=0.0264, p99=0.0399, avg=0.0094
- Status counts: `200:120`

### Post view (no tags) id=49970

- URL: `http://localhost:4000/api/post/49970?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0071, p95=0.0121, p99=0.0179, avg=0.0075
- Status counts: `200:120`

### Post view (no tags) id=49967

- URL: `http://localhost:4000/api/post/49967?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0097, p95=0.0384, p99=0.0609, avg=0.0146
- Status counts: `200:120`

### Post view (few tags) id=49995

- URL: `http://localhost:4000/api/post/49995?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0147, p95=0.0473, p99=0.0618, avg=0.0182
- Status counts: `200:120`

### Post view (few tags) id=49994

- URL: `http://localhost:4000/api/post/49994?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0148, p95=0.0434, p99=0.0860, avg=0.0198
- Status counts: `200:120`

### Post view (few tags) id=49993

- URL: `http://localhost:4000/api/post/49993?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0128, p95=0.0304, p99=0.0374, avg=0.0157
- Status counts: `200:120`

### Post view (few tags) id=49976

- URL: `http://localhost:4000/api/post/49976?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0109, p95=0.0213, p99=0.0274, avg=0.0119
- Status counts: `200:120`

### Post view (few tags) id=49973

- URL: `http://localhost:4000/api/post/49973?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0119, p95=0.0171, p99=0.0215, avg=0.0120
- Status counts: `200:120`

### Post view (many tags) id=50000

- URL: `http://localhost:4000/api/post/50000?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0090, p95=0.0145, p99=0.0213, avg=0.0093
- Status counts: `200:120`

### Post view (many tags) id=49998

- URL: `http://localhost:4000/api/post/49998?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0084, p95=0.0121, p99=0.0186, avg=0.0085
- Status counts: `200:120`

### Post view (many tags) id=49997

- URL: `http://localhost:4000/api/post/49997?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0099, p95=0.0229, p99=0.0730, avg=0.0131
- Status counts: `200:120`

### Post view (many tags) id=49992

- URL: `http://localhost:4000/api/post/49992?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0114, p95=0.0227, p99=0.0319, avg=0.0122
- Status counts: `200:120`

### Post view (many tags) id=49988

- URL: `http://localhost:4000/api/post/49988?fields=id%2Cversion%2CcreationTime%2ClastEditTime%2Csafety%2Csource%2Ctype%2CmimeType%2Cchecksum%2CchecksumMD5%2CfileSize%2CcanvasWidth%2CcanvasHeight%2Cduration%2CcontentUrl%2CthumbnailUrl%2Cflags%2Ctags%2Crelations%2Cuser%2Cscore%2CownScore%2CownFavorite%2CfavoriteCount%2CcommentCount%2Cnotes%2Ccomments`
- Iterations: `120`
- Concurrency: `5`
- Latency (seconds): p50=0.0124, p95=0.0336, p99=0.0523, avg=0.0155
- Status counts: `200:120`
