<% if (ctx.postFlow) { %><div class='post-list post-flow'><% } else { %><div class='post-list'><% } %>
    <% if (ctx.response.results.length) { %>
        <ul>
            <%
            const useBackgroundImage = ctx.layoutType === "default";
            for (const post of ctx.response.results) {
                const postTags = ctx.excludeRedundantTags(post.tags);
                let postTitle = postTags.map(tag => tag.names[0]).join(' ') || '(no tags)';
                if (post.type === "video") {
                    postTitle = `(video)\n\n${postTitle}`;
                }
            %>
                <li data-post-id='<%= post.id %>'>
                    <a class='thumbnail-wrapper <%= post.tags.length > 2 ? "tags" : "no-tags" %>'
                            title='<%- postTitle %>'
                            href='<%= ctx.getPostUrl(post.id, ctx.parameters) %>'>
                        <%= ctx.makeThumbnail(post.thumbnailUrl, useBackgroundImage) %>
                        <% if (post.type === 'video') { %>
                            <span class='type' data-type='<%- post.type %>'>
                                <span class='icon'><i class='la la-video'></i></span>
                            </span>
                        <% } %>
                        <% if (post.score || post.favoriteCount || post.commentCount) { %>
                            <span class='stats'>
                                <% if (post.score) { %>
                                    <span class='icon post-score'>
                                        <i class='la la-thumbs-up'></i>
                                        <%- post.score %>
                                    </span>
                                <% } %>
                                <% if (post.favoriteCount) { %>
                                    <span class='icon post-favorites'>
                                        <i class='la la-heart'></i>
                                        <%- post.favoriteCount %>
                                    </span>
                                <% } %>
                                <% if (post.commentCount) { %>
                                    <span class='icon post-comments'>
                                        <i class='lar la-comment-dots'></i>
                                        <%- post.commentCount %>
                                    </span>
                                <% } %>
                            </span>
                        <% } %>
                    </a>
                    <span class='edit-overlay'>
                        <% if (ctx.canBulkEditTags && ctx.parameters && ctx.parameters.tag) { %>
                            <a class='tag-flipper'>
                            </a>
                        <% } %>
                        <% if (ctx.parameters && ctx.parameters.relations) { %>
                            <a class='relation-flipper'>
                            </a>
                        <% } %>
                        <% if (ctx.canBulkEditSafety && ctx.parameters && ctx.parameters.safety) { %>
                            <span class='safety-flipper'>
                                <% for (let safety of ['safe', 'sketchy', 'unsafe']) { %>
                                    <a data-safety='<%- safety %>' class='safety-<%- safety %><%- post.safety === safety ? ' active' : '' %>'>
                                    </a>
                                <% } %>
                            </span>
                        <% } %>
                        <% if (ctx.canBulkDelete && ctx.parameters && ctx.parameters.delete) { %>
                            <a class='delete-flipper'>
                            </a>
                        <% } %>
                    </span>
                </li>
            <% } %>
            <% if (ctx.addFlexAlignment) { %>
                <%= ctx.makeFlexboxAlign() %>
            <% } %>
        </ul>
    <% } %>
</div>
