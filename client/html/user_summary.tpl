<div id='user-summary'>
    <%= ctx.makeThumbnail(ctx.user.avatarUrl) %>
    <ul class='basic-info'>
        <li>Registered: <%= ctx.makeRelativeTime(ctx.user.creationTime) %></li>
        <% if (ctx.canEditAnything) { %>
            <li>Last seen: <%= ctx.makeRelativeTime(ctx.user.lastLoginTime) %></li>
        <% } %>
        <li>Rank: <%- ctx.user.rankName.toLowerCase() %></li>
    </ul>

    <div>
        <nav>
            <p><strong>Quick links</strong></p>
            <ul>
                <li><a href='<%- ctx.formatPostsLink({q: 'submit:' + ctx.user.name}) %>'><%- ctx.user.uploadedPostCount %> uploads</a></li>
                <li><a href='<%- ctx.formatPostsLink({q: 'fav:' + ctx.user.name}) %>'><%- ctx.user.favoritePostCount %> favorites</a></li>
                <li><a href='<%- ctx.formatPostsLink({q: 'comment:' + ctx.user.name}) %>'><%- ctx.user.commentCount %> comments</a></li>
            </ul>
        </nav>

        <% if (ctx.isLoggedIn) { %>
            <nav>
                <p><strong>Only visible to you</strong></p>
                <ul>
                    <li><a href='<%- ctx.formatPostsLink({q: 'special:liked'}) %>'><%- ctx.user.likedPostCount %> liked posts</a></li>
                    <li><a href='<%- ctx.formatPostsLink({q: 'special:disliked'}) %>'><%- ctx.user.dislikedPostCount %> disliked posts</a></li>
                </ul>
            </nav>
        <% } %>
    </div>
</div>
