<% if (ctx.canFavorite) { %>
    <% if (ctx.ownFavorite) { %>
        <a class='remove-favorite'>
            <i class='la la-heart'></i>
    <% } else { %>
        <a class='add-favorite'>
            <i class='lar la-heart'></i>
    <% } %>
<% } else { %>
    <a class='add-favorite inactive'>
        <i class='lar la-heart'></i>
<% } %>
    <span class='vim-nav-hint'>add to favorites</span>
</a>
<span class='value'><%- ctx.favoriteCount %></span>
