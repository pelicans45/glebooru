<li><!--
--><% if (ctx.editMode) { %><!--
    --><a class='remove-metric' data-pseudo-content='×'/><!--
    --><a href="<%- ctx.formatPostsLink({
                q: 'metric-' + ctx.escapeTagName(ctx.tag.names[0]) +
                    ':' + ctx.tag.metric.min + '..' + ctx.tag.metric.max +
                    ' sort:metric-' + ctx.escapeTagName(ctx.tag.names[0])
                }) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><i class='las la-angle-right tag-icon'></i><!--
        --><%- ctx.postMetric.tagName %>:</a><!--
    --><%= ctx.makeNumericInput({
           name: 'value',
           value: ctx.postMetric.value,
           step: 'any',
           min: ctx.tag.metric.min,
           max: ctx.tag.metric.max,
       }) %><!--
--><% } else { %><!--
    --><a href="<%- ctx.formatClientLink('tag', ctx.tag.names[0]) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><i class='las la-angle-right tag-icon'></i><!--
    --></a><!--
    --><a href="<%- ctx.formatPostsLink({
                q: 'metric-' + ctx.escapeTagName(ctx.tag.names[0]) +
                    ':' + ctx.tag.metric.min + '..' + ctx.tag.metric.max +
                    ' sort:metric-' + ctx.escapeTagName(ctx.tag.names[0])
                }) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><%- ctx.postMetric.tagName %>: <%- ctx.postMetric.value || 0 %></a><!--
--><% } %><!--
--></li>
