<div class='readonly-sidebar'>
    <article class='details'>
        <section class='download'>
            <a rel='external' href='<%- ctx.post.contentUrl %>' download='<%- ctx.post.getDownloadFilename() %>'>
                <i class='la la-download'></i>
                <!--
                <span style="display: none">
                <%= ctx.makeFileSize(ctx.post.fileSize) %>
                <%- {
                    'image/gif': 'GIF',
                    'image/jpeg': 'JPEG',
                    'image/png': 'PNG',
                    'image/webp': 'WEBP',
                    'image/bmp': 'BMP',
                    'image/avif': 'AVIF',
                    'image/heif': 'HEIF',
                    'image/heic': 'HEIC',
                    'video/webm': 'WEBM',
                    'video/mp4': 'MPEG-4',
                    'video/quicktime': 'MOV',
                    'application/x-shockwave-flash': 'SWF',
                }[ctx.post.mimeType] %>
                </span>
                -->
            </a>
            <span class='dims'><%- ctx.post.canvasWidth %>x<%- ctx.post.canvasHeight %></span>
            <!--
            <% if (ctx.post.flags.length) { %>
                <% if (ctx.post.flags.includes('loop')) { %><i class='la la-redo-alt'></i><% } %>
                <% if (ctx.post.flags.includes('sound')) { %><i class='la la-volume-up'></i><% } %>
            <% } %>
            -->
        </section>

        <section class='upload-info'>
            <%= ctx.makeUserLinkForSidebar(ctx.post.user) %>
            <%= ctx.makeRelativeTime(ctx.post.creationTime) %>
        </section>

        <% if (ctx.enableSafety) { %>
            <section class='safety'>
                <i class='la la-circle safety-<%- ctx.post.safety %>'></i><!--
                --><%- ctx.post.safety[0].toUpperCase() + ctx.post.safety.slice(1) %>
            </section>
        <% } %>

        <section class='zoom'>
            <a class='fit-original'>Original zoom</a> &middot;
            <a class='fit-width'>fit width</a> &middot;
            <a class='fit-height'>height</a> &middot;
            <a class='fit-both'>both</a>
        </section>

        <% if (ctx.post.source) { %>
            <section class='source'>
                Source: <% for (let i = 0; i < ctx.post.sourceSplit.length; i++) { %>
                    <% if (i != 0) { %>&middot;<% } %>
                    <a href='<%- ctx.post.sourceSplit[i] %>' title='<%- ctx.post.sourceSplit[i] %>'><%- ctx.extractRootDomain(ctx.post.sourceSplit[i]) %></a>
                <% } %>
            </section>
        <% } %>

        <section class='search'>
            Search on
            <a target="_blank" href='http://iqdb.org/?url=<%- encodeURIComponent(ctx.post.fullContentUrl) %>'>IQDB</a> &middot;
            <a target="_blank" href='https://danbooru.donmai.us/posts?tags=md5:<%- ctx.post.checksumMD5 %>'>Danbooru</a> &middot;
            <a target="_blank" href='https://www.google.com/searchbyimage?&image_url=<%- encodeURIComponent(ctx.post.fullContentUrl) %>'>Google Images</a>
        </section>

        <section class='social'>
            <div class='score-container'></div>
            <div class='fav-container'></div>
        </section>
    </article>

    <% if (ctx.post.relations.length) { %>
        <nav class='relations'>
            <h1>Relations</h1>
            <ul><!--
                --><% for (let post of ctx.post.relations) { %><!--
                    --><li><!--
                        --><a href='<%= ctx.getPostUrl(post.id, ctx.parameters) %>'><!--
                            --><%= ctx.makeThumbnail(post.thumbnailUrl) %><!--
                        --></a><!--
                    --></li><!--
                --><% } %><!--
            --></ul>
        </nav>
    <% } %>

    <nav class='tags'>
        <!-- <h1>Tags</h1> -->
        <% if (ctx.tags.length) { %>
            <ul class='compact-tags'><!--
                --><% for (let tag of ctx.tags) { %><!--
                    --><li><!--
                        --><% if (ctx.canViewTags) { %><!--
                        --><a href='<%- ctx.formatClientLink('tag', tag.names[0]) %>' class='tag-link-info <%= ctx.makeCssName(tag.category, 'tag') %>'><!--
                            --><i class='la la-tag'></i><!--
                        --><% } %><!--
                        --><% if (ctx.canViewTags) { %><!--
                            --></a><!--
                        --><% } %><!--
                        --><% if (ctx.canListPosts) { %><!--
                            --><a href='<%- ctx.formatPostsLink({q: ctx.escapeTagName(tag.names[0])}) %>' class='tag-link-posts <%= ctx.makeCssName(tag.category, 'tag') %>' title='(<%- tag.category %>)'><!--
                        --><% } %><!--
                            --><%- ctx.getPrettyName(tag.names[0]) %>&#32;<!--
                        --><% if (ctx.canListPosts) { %><!--
                            --></a><!--
                        --><% } %><!--
                        --><span class='tag-usages' data-pseudo-content='<%- tag.postCount %>'></span><!--
                    --></li><!--
                --><% } %><!--
            --></ul>
        <% } else { %>
            <p>
                No tags yet
                <% if (ctx.canEditPosts) { %>
                    <a href='<%= ctx.getPostEditUrl(ctx.post.id, ctx.parameters) %>'>Add tags</a>
                <% } %>
            </p>
        <% } %>
    </nav>

    <% if (ctx.post.metrics.length + ctx.post.metricRanges.length) { %>
        <nav class='metrics'>
            <h1>Metrics (<%- ctx.post.metrics.length + ctx.post.metricRanges.length %>)</h1>
            <ul class='compact-post-metrics'></ul>
        </nav>
    <% } %>

    <% if (ctx.canViewSimilar) { %>
        <nav class='similar'>
            <h1>Similar</h1>
            <ul></ul>
            <a href='<%- ctx.formatPostsLink({q: "similar:" + ctx.post.id}) %>'>See more</a>
        </nav>

        <nav class='lookalikes'>
            <h1>Lookalikes</h1>
            <ul></ul>
        </nav>
    <% } %>
</div>
