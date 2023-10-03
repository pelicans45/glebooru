# glebooru

glebooru is a modern booru. It's a fork of [szurubooru](https://github.com/rr-/szurubooru), with many additions implemented from [Hunternif's fork](https://github.com/Hunternif/szurubooru) and [po5's fork](https://github.com/po5/szurubooru/tree/vb).

## Features

- Post content: images (JPG, PNG, GIF, animated GIF), videos (MP4, WEBM), Flash animations
- Ability to retrieve web video content using [youtube-dl](https://github.com/ytdl-org/youtube-dl)
- Post comments
- Post notes / annotations, including arbitrary polygons
- Rich JSON REST API ([see documentation](doc/API.md))
- Token based authentication for clients
- Rich search system
- Rich privilege system
- Autocomplete in search and while editing tags
- Tag categories
- Tag suggestions
- Tag implications (adding a tag automatically adds another)
- Tag aliases
- Pools and pool categories
- Duplicate detection
- Post rating and favoriting; comment rating
- Polished UI
- Browser configurable endless paging
- Browser configurable backdrop grid for transparent images


## Development

Add the following to your hosts file:

```
127.0.0.1 booru
127.0.0.1 bfilter
```

Run `./d` to start the development Docker containers. Pass `-w` to `./d` to live-recompile client-side files.
