<li><!--
--><% if (ctx.editMode) { %><!--
    --><a href="<%- ctx.formatClientLink('tag', ctx.tag.names[0]) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><i class='fa fa-sliders-h tag-icon'></i><!--
    --></a><!--
    --><a href="<%- ctx.formatClientLink('posts', {
                query: 'metric-' + ctx.escapeColons(ctx.tag.names[0]) +
                    ':' + ctx.tag.metric.min + '..' + ctx.tag.metric.max
                }) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><%- ctx.tag.names[0] %>&#32;<!--
    --></a><!--
    --><span class='metric-bounds' data-pseudo-content=
    '<%- ctx.tag.metric.min %> &mdash; <%- ctx.tag.metric.max %>'></span><!--
    --><span class='metric-controls'>Set<!--
        --><a class='create-exact'> exact</a><!--
        --><a class='create-range'> range</a><!--
    --></span><!--
--><% } %><!--
--></li>
