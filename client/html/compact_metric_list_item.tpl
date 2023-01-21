<li><!--
--><% if (ctx.editMode) { %><!--
    --><a href="<%- ctx.formatClientLink('tag', ctx.tag.names[0]) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><i class='la la-sliders-h tag-icon'></i><!--
    --></a><!--
    --><a href="<%- ctx.formatPostsLink({
                query: 'metric-' + ctx.escapeTagName(ctx.tag.names[0]) +
                    ':' + ctx.tag.metric.min + '..' + ctx.tag.metric.max +
                    ' sort:metric-' + ctx.escapeTagName(ctx.tag.names[0])
                }) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><%- ctx.tag.names[0] %>&#32;<!--
    --></a><!--
    --><span class='metric-bounds' data-pseudo-content=
    '<%- ctx.tag.metric.min %> &mdash; <%- ctx.tag.metric.max %>'></span><!--
    --><span class='metric-controls'>Set<!--
        --><a class='create-exact'> exact</a><!--
        --><a class='create-range'> range</a><!--
        --><a href='<%= ctx.getMetricSorterUrl(ctx.post.id, {
                    metrics: ctx.tag.names[0],
                    query: ctx.query}) %>'
               class='sort'> sort</a><!--
    --></span><!--
--><% } %><!--
--></li>
