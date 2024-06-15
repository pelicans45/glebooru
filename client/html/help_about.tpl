<p><%- ctx.description %></p>

<hr>

<% if (!ctx.isUniversal) { %>
<p>
<a href="https://<%- ctx.universalHostname %>">Main hub</a>
</p>
<hr>
<% } %>

<!--
<p>
<a href="">Source code</a>
</p>
-->
