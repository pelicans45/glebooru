<% if (ctx.canFavorite) { %>
    <% if (ctx.ownFavorite) { %>
        <a class='remove-favorite' title='Favorite'>
            <i class='la la-heart'></i>
    <% } else { %>
        <a class='add-favorite' title='Favorite'>
            <i class='lar la-heart'></i>
    <% } %>
<% } else { %>
    <a class='add-favorite inactive'>
        <i class='lar la-heart'></i>
<% } %>
</a>
<span class='value'><%- ctx.favoriteCount %></span>
