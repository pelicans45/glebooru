<div class='readonly-sidebar'>
    <article class='details'>
        <section class='social'>
            <div class='score-container'></div>
            <div class='fav-container'></div>
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
            <% const base64md5 = encodeURIComponent(ctx.post.checksumMD5Base64); %>
            Search
            <a target="_blank" href='https://archived.moe/_/search/image/<%- base64md5 %>'>moe</a> &middot;
            <a target="_blank" href='https://archive.4plebs.org/_/search/image/<%- base64md5 %>'>4plebs</a> &middot;
            <a target="_blank" href='https://desuarchive.org/_/search/image/<%- base64md5 %>'>desuarchive</a>
        </section>
        <% if (window.innerWidth <= 800) { %>
            <nav class='tags'>
                <!-- <h2>Tags</h2> -->
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
                                    --><%- ctx.getPrettyName(tag.names[0]) %><!--
                                --><% if (ctx.canListPosts) { %><!--
                                    --></a><!--
                                --><% } %>&#32;<!--
                                --><span class='tag-usages' data-pseudo-content='<%- tag.postCount %>'></span><!--
                            --></li><!--
                        --><% } %><!--
                    --></ul>
                <% } else { %>
                    <p>
                        No tags yet
                        <br>
                        <% if (ctx.canEditPosts) { %>
                            <a href='<%= ctx.getPostEditUrl(ctx.post.id, ctx.parameters) %>' title='Add tags'>Add tags</a>
                        <% } %>
                    </p>
                <% } %>
            </nav>
        <% } %>
    </article>

    <% if (ctx.post.relations.length) { %>
        <nav class='relations'>
            <h2>Relations</h2>
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
    <% if (window.innerWidth >= 801) { %>
        <nav class='tags'>
            <!-- <h2>Tags</h2> -->
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
                                --><a href='<%- ctx.formatPostsLink({q: ctx.escapeTagName(tag.names[0])}) %>' class='tag-link-posts <%= ctx.makeCssName(tag.category, 'tag') %>' title='(<%- tag.category.replace("_", " ") %>)'><!--
                            --><% } %><!--
                                --><%- ctx.getPrettyName(tag.names[0]) %><!--
                            --><% if (ctx.canListPosts) { %><!--
                                --></a><!--
                            --><% } %>&#32;<!--
                            --><span class='tag-usages' data-pseudo-content='<%- tag.postCount %>'></span><!--
                        --></li><!--
                    --><% } %><!--
                --></ul>
            <% } else { %>
                <p>
                    No tags yet
                    <br>
                    <% if (ctx.canEditPosts) { %>
                        <a href='<%= ctx.getPostEditUrl(ctx.post.id, ctx.parameters) %>'>Add tags</a>
                    <% } %>
                </p>
            <% } %>
        </nav>
    <% } %>

    <% /* if (ctx.post.metrics.length + ctx.post.metricRanges.length) { %>
        <nav class='metrics'>
            <h2>Metrics (<%- ctx.post.metrics.length + ctx.post.metricRanges.length %>)</h2>
            <ul class='compact-post-metrics'></ul>
        </nav>
    <% } */ %>

    <% if (ctx.canViewSimilar) { %>
        <nav class='similar'>
            <h2>Similar</h2>
            <ul></ul>
            <a href='<%- ctx.formatPostsLink({q: "similar:" + ctx.post.id + " -id:" + ctx.post.id}) %>' title='View similar images' >See more</a>
        </nav>

        <nav class='lookalikes'>
            <h2>Lookalikes</h2>
            <ul></ul>
        </nav>
    <% } %>
</div>
