<li>
    <a href="<%- ctx.formatClientLink('posts', {
                query: 'metric-' + ctx.escapeColons(ctx.metric.tag.names[0]) +
                    ':' + ctx.metric.min + '..' + ctx.metric.max +
                    ' sort:metric-' + ctx.escapeColons(ctx.metric.tag.names[0])
                }) %>"
       class="<%= ctx.makeCssName(ctx.metric.tag.category, 'tag') %>"><%
        %><%- ctx.metric.tag.names[0] %></a>
</li>