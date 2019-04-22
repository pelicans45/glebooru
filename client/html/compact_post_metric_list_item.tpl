<li><!--
--><% if (ctx.editMode) { %><!--
    --><a href="<%- ctx.formatClientLink('tag', ctx.postMetric.tagName) %>"
          class="<%= ctx.makeCssName(ctx.tag.category, 'tag') %>"><!--
        --><i class='fas fa-angle-right tag-icon'></i><!--
    --><%- ctx.postMetric.tagName %>: </a><!--
    --><%= ctx.makeNumericInput({
           name: 'value',
           value: ctx.postMetric.value,
           step: 'any',
           min: ctx.tag.metric.min,
           max: ctx.tag.metric.max,
       }) %><!--
--><% } %><!--
--></li>

