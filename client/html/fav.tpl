<% if (ctx.canFavorite) { %>
    <% if (ctx.ownFavorite) { %>
        <a class='remove-favorite'>
            <i class='fa fa-heart'></i>
    <% } else { %>
        <a class='add-favorite'>
            <i class='far fa-heart'></i>
    <% } %>
<% } else { %>
    <a class='add-favorite inactive'>
        <i class='far fa-heart'></i>
<% } %>
    <span class='vim-nav-hint'>add to favorites</span>
</a>
<span class='value'><%- ctx.favoriteCount %></span>
