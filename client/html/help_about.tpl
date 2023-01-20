<p><%- ctx.description %></p>

<hr>

<% if (!ctx.isUniversal) { %>
<p>
<a href="https://<%- ctx.universalHostname %>">Main hub</a>
</p>
<hr>
<% } %>

<p>
<a href="https://github.com/parallax4/glebooru">Source code</a>
</p>
