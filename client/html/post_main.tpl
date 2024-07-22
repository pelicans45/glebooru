<div class='content-wrapper transparent post-view'>
    <% if (window.innerWidth >= 801) { %>
        <aside class='sidebar'>
            <nav class='buttons'>
                <article class='previous-post' title='Previous'>
                    <% if (ctx.prevPostId) { %>
                        <% if (ctx.editMode) { %>
                            <a rel='prev' href='<%= ctx.getPostEditUrl(ctx.prevPostId, ctx.parameters) %>'>
                        <% } else { %>
                            <a rel='prev' href='<%= ctx.getPostUrl(ctx.prevPostId, ctx.parameters) %>'>
                        <% } %>
                    <% } else { %>
                        <a rel='prev' class='inactive'>
                    <% } %>
                        <i class='la la-chevron-left'></i>
                    </a>
                </article>
                <article class='next-post' title='Next'>
                    <% if (ctx.nextPostId) { %>
                        <% if (ctx.editMode) { %>
                            <a rel='next' href='<%= ctx.getPostEditUrl(ctx.nextPostId, ctx.parameters) %>'>
                        <% } else { %>
                            <a rel='next' href='<%= ctx.getPostUrl(ctx.nextPostId, ctx.parameters) %>'>
                        <% } %>
                    <% } else { %>
                        <a rel='next' class='inactive'>
                    <% } %>
                        <i class='la la-chevron-right'></i>
                    </a>
                </article>
                <article class='random-post' title='Random image'>
                    <% if (ctx.randomPostId) { %>
                        <% if (ctx.editMode) { %>
                            <a rel='next' href='<%= ctx.getPostEditUrl(ctx.randomPostId, {
                                q: ctx.parameters.q,
                                metrics: ctx.parameters.metrics,
                                r: Math.round(Math.random() * 998) + 1}) %>'>
                        <% } else { %>
                            <a rel='next' href='<%= ctx.getPostUrl(ctx.randomPostId, {
                                q: ctx.parameters.q,
                                metrics: ctx.parameters.metrics,
                                r: Math.round(Math.random() * 998) + 1}) %>'>
                        <% } %>
                    <% } else { %>
                        <a rel='next' class='inactive'>
                    <% } %>
                        <i title='Random image' class='la la-random'></i>
                    </a>
                </article>
                <article class='edit-post' title='Edit'>
                    <% if (ctx.editMode) { %>
                        <a href='<%= ctx.getPostUrl(ctx.post.id, ctx.parameters) %>'>
                            <i class='la la-reply'></i>
                        </a>
                    <% } else { %>
                        <% if (ctx.canEditPosts || ctx.canDeletePosts || ctx.canFeaturePosts) { %>
                            <a href='<%= ctx.getPostEditUrl(ctx.post.id, ctx.parameters) %>'>
                            <i class='la la-pencil-alt'></i>
                            </a>
                        <% } %>
                    <% } %>
                </article>
            </nav>
            <div class='sidebar-container'></div>
            <% if (ctx.canCreateComments) { %>
                <a id='add-comment-button' title='Add a comment'><h3>Add comment</h3></a>
            <% } %>
        </aside>
    <% } %>
    <% if (window.innerWidth >= 801) { %>
        <article class='download' title='Download'>
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
        </article>
    <% } %>

    <div class='content'>
        <div class='post-container'></div>
        <% if (window.innerWidth <= 800) { %>
            <nav class='buttons'>
                <article class='previous-post' title='Previous'>
                    <% if (ctx.prevPostId) { %>
                        <% if (ctx.editMode) { %>
                            <a rel='prev' href='<%= ctx.getPostEditUrl(ctx.prevPostId, ctx.parameters) %>'>
                        <% } else { %>
                            <a rel='prev' href='<%= ctx.getPostUrl(ctx.prevPostId, ctx.parameters) %>'>
                        <% } %>
                    <% } else { %>
                        <a rel='prev' class='inactive'>
                    <% } %>
                        <i class='la la-chevron-left'></i>
                    </a>
                </article>
                <article class='next-post' title='Next'>
                    <% if (ctx.nextPostId) { %>
                        <% if (ctx.editMode) { %>
                            <a rel='next' href='<%= ctx.getPostEditUrl(ctx.nextPostId, ctx.parameters) %>'>
                        <% } else { %>
                            <a rel='next' href='<%= ctx.getPostUrl(ctx.nextPostId, ctx.parameters) %>'>
                        <% } %>
                    <% } else { %>
                        <a rel='next' class='inactive'>
                    <% } %>
                        <i class='la la-chevron-right'></i>
                    </a>
                </article>
                <article class='random-post' title='Random image'>
                    <% if (ctx.randomPostId) { %>
                        <% if (ctx.editMode) { %>
                            <a rel='next' href='<%= ctx.getPostEditUrl(ctx.randomPostId, {
                                q: ctx.parameters.q,
                                metrics: ctx.parameters.metrics,
                                r: Math.round(Math.random() * 998) + 1}) %>'>
                        <% } else { %>
                            <a rel='next' href='<%= ctx.getPostUrl(ctx.randomPostId, {
                                q: ctx.parameters.q,
                                metrics: ctx.parameters.metrics,
                                r: Math.round(Math.random() * 998) + 1}) %>'>
                        <% } %>
                    <% } else { %>
                        <a rel='next' class='inactive'>
                    <% } %>
                        <i title='Random image' class='la la-random'></i>
                    </a>
                </article>
                <article class='edit-post' title='Edit'>
                    <% if (ctx.editMode) { %>
                        <a href='<%= ctx.getPostUrl(ctx.post.id, ctx.parameters) %>'>
                            <i class='la la-reply'></i>
                        </a>
                    <% } else { %>
                        <% if (ctx.canEditPosts || ctx.canDeletePosts || ctx.canFeaturePosts) { %>
                            <a href='<%= ctx.getPostEditUrl(ctx.post.id, ctx.parameters) %>'>
                            <i class='la la-pencil-alt'></i>
                            </a>
                        <% } %>
                    <% } %>
                </article>
                <article class='download' title='Download'>
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
                </article>
            </nav>
            <aside class='sidebar'>
                <div class='sidebar-container'></div>
                <% if (ctx.canCreateComments) { %>
                    <a id='add-comment-button' title='Add a comment'><h3>Add comment</h3></a>
                <% } %>
            </aside>
        <% } %>
        <% if (ctx.canListComments) { %>
            <div class='comments-container'></div>
        <% } %>

        <% if (ctx.canCreateComments) { %>
            <div class='comment-form-container'></div>
        <% } %>
    </div>
</div>
