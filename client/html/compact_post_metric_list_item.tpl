<li><!--
--><% if (ctx.editMode) { %><!--
    --><a href="<%- ctx.formatClientLink('posts', {
                query: 'metric-' + ctx.escapeColons(ctx.postMetric.tagName) +
                    ':' + ctx.postMetric.value
                }) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><i class='fas fa-angle-right tag-icon'></i><!--
        --><%- ctx.postMetric.tagName %>:</a><!--
    --><%= ctx.makeNumericInput({
           name: 'value',
           value: ctx.postMetric.value,
           step: 'any',
           min: ctx.tag.metric.min,
           max: ctx.tag.metric.max,
       }) %><!--
--><% } else { %><!--
    --><a href="<%- ctx.formatClientLink('tag', ctx.postMetric.tagName, 'metric') %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><i class='fas fa-angle-right tag-icon'></i><!--
    --></a><!--
    --><a href="<%- ctx.formatClientLink('posts', {
            query: 'metric-' + ctx.escapeColons(ctx.postMetric.tagName) +
                ':' + ctx.postMetric.value
            }) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><%- ctx.postMetric.tagName %>: <%- ctx.postMetric.value || 0 %></a><!--
--><% } %><!--
--></li>
