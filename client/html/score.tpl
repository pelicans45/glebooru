<% if (ctx.canScore) { %>
    <a href class='upvote'>
        <% if (ctx.ownScore == 1) { %>
            <i class='fa fa-thumbs-up'></i>
        <% } else { %>
            <i class='far fa-thumbs-up'></i>
        <% } %>
        <span class='vim-nav-hint'>upvote</span>
        <span class='vim-nav-hint'>like</span>
    </a>
<% } else { %>
    <a class='upvote inactive'>
        <i class='far fa-thumbs-up'></i>
    </a>
<% } %>
<span class='value'><%- ctx.score %></span>
<% if (ctx.canScore) { %>
    <a href class='downvote'>
        <% if (ctx.ownScore == -1) { %>
            <i class='fa fa-thumbs-down'></i>
        <% } else { %>
            <i class='far fa-thumbs-down'></i>
        <% } %>
        <span class='vim-nav-hint'>downvote</span>
        <span class='vim-nav-hint'>dislike</span>
    </a>
<% } %>
