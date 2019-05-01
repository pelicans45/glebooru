<header>
    <% if (ctx.post) { %>
        <label>Post #<%- ctx.post.id %></label>
    <% } %>
</header>

<% if (ctx.post) { %>
    <div class='post-container'></div>
<% } %>
