<div class='content-wrapper transparent post-view'>
    <aside class='sidebar'>
        <nav class='buttons'>
            <article class='previous-post'>
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
                    <span class='vim-nav-hint'>&lt; Previous</span>
                </a>
            </article>
            <article class='next-post'>
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
                    <span class='vim-nav-hint'>Next &gt;</span>
                </a>
            </article>
            <article class='random-post'>
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
                    <span class='vim-nav-hint'>Random image</span>
                </a>
            </article>
            <article class='edit-post'>
                <% if (ctx.editMode) { %>
                    <a href='<%= ctx.getPostUrl(ctx.post.id, ctx.parameters) %>'>
                        <i class='la la-reply'></i>
                        <span class='vim-nav-hint'>Back to view mode</span>
                    </a>
                <% } else { %>
                    <% if (ctx.canEditPosts || ctx.canDeletePosts || ctx.canFeaturePosts) { %>
                        <a href='<%= ctx.getPostEditUrl(ctx.post.id, ctx.parameters) %>'>
                        <i class='la la-pencil-alt'></i>
                        <span class='vim-nav-hint'>Edit</span>
                        </a>
                    <% } %>
                <% } %>
            </article>
        </nav>

        <div class='sidebar-container'></div>

        <% if (screen.width <= 1000) { %>
            <div class='comments-panel'>
                <% if (ctx.canListComments) { %>
                    <div class='comments-container'></div>
                <% } %>
                <% if (ctx.canCreateComments) { %>
                    <a id='add-comment-button'><h3>Add comment</h3></a>
                    <div class='comment-form-container'></div>
                <% } %>
            </div>
        <% } %>
    </aside>

    <div class='content'>
        <div class='post-container'></div>

        <% if (screen.width > 1000) { %>
            <% if (ctx.canListComments) { %>
                <div class='comments-container'></div>
            <% } %>

            <% if (ctx.canCreateComments) { %>
                <a id='add-comment-button'><h3>Add comment</h3></a>
                <div class='comment-form-container'></div>
            <% } %>
        <% } %>
    </div>
</div>
