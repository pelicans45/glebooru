<ul>
    <li><%- ctx.postCount %> posts</li><span class='sep'>
    </span><li><%= ctx.makeFileSize(ctx.diskUsage) %></li><span class='sep'>
    </span><% if (ctx.canListSnapshots) { %><li><a href='<%- ctx.formatClientLink('history') %>'>History</a></li><span class='sep'>
    </span><% } %>
</ul>
