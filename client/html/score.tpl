<% if (ctx.canScore) { %>
    <a class='upvote'>
        <% if (ctx.ownScore == 1) { %>
            <i class='la la-thumbs-up'></i>
        <% } else { %>
            <i class='lar la-thumbs-up'></i>
        <% } %>
        <span class='vim-nav-hint'>upvote</span>
        <span class='vim-nav-hint'>like</span>
    </a>
<% } else { %>
    <a class='upvote inactive'>
        <i class='lar la-thumbs-up'></i>
    </a>
<% } %>
<span class='value'><%- ctx.score %></span>
<% if (ctx.canScore) { %>
    <a class='downvote'>
        <% if (ctx.ownScore == -1) { %>
            <i class='la la-thumbs-down'></i>
        <% } else { %>
            <i class='lar la-thumbs-down'></i>
        <% } %>
        <span class='vim-nav-hint'>downvote</span>
        <span class='vim-nav-hint'>dislike</span>
    </a>
<% } %>
