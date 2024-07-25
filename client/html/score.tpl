<% if (ctx.canScore) { %>
    <a class='upvote' title='Like'>
        <% if (ctx.ownScore == 1) { %>
            <i class='la la-thumbs-up'></i>
        <% } else { %>
            <i class='lar la-thumbs-up'></i>
        <% } %>
    </a>
<% } else { %>
    <a class='upvote inactive'>
        <i class='lar la-thumbs-up'></i>
    </a>
<% } %>
<span class='value'><%- ctx.score %></span>
<% if (ctx.canScore) { %>
    <a class='downvote' title='Dislike'>
        <% if (ctx.ownScore == -1) { %>
            <i class='la la-thumbs-down'></i>
        <% } else { %>
            <i class='lar la-thumbs-down'></i>
        <% } %>
    </a>
<% } else { %>
    <a class='downvote inactive'>
        <i class='lar la-thumbs-down'></i>
    </a>
<% } %>