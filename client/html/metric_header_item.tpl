<li class="<%= ctx.makeCssName(ctx.metric.tag.category, 'tag') %><%
            if (ctx.selected) { %> selected<% } %>">
    <a class="<%= ctx.makeCssName(ctx.metric.tag.category, 'tag') %><%
            if (ctx.selected) { %> selected<% } %>"><%
        %><%- ctx.metric.tag.names[0] %></a>
</li>