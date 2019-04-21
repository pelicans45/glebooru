<div class='metric-input'>
    <% if (ctx.tags.filterMetrics().length) { %>
        <ul class='compact-unset-metrics'><!--
        --><% for (let tag of ctx.tags.filterMetrics()) { %><!--
            --><li><!--
                --><a href="<%- ctx.formatClientLink('tag', tag.names[0], 'metric') %>"
                      class="<%= ctx.makeCssName(tag.category, 'tag') %>"><!--
                    --><i class='fa fa-arrows-alt-h'></i><!--
                --></a><!--
                --><a href="<%- ctx.formatClientLink('posts', {
                            query: 'metric-' + ctx.escapeColons(tag.names[0]) +
                                ':' + tag.metric.min + '..' + tag.metric.max
                            }) %>"
                      class="<%= ctx.makeCssName(tag.category, 'tag') %>"><!--
                    --><%- tag.names[0] %>&#32;<!--
                --></a><!--
                --><span class='metric-bounds' data-pseudo-content=
        '<%- tag.metric.min %> &mdash; <%- tag.metric.max %>'></span><!--
                --><span class='metric-controls'>Set <!--
                    --><a class='create-exact'>exact</a> <!--
                    --><a class='create-range'>range</a><!--
                --></span><!--
            --></li><!--
        --><% } %><!--
        --></ul>
        <% if (ctx.postMetrics.length) { %><hr><% } %>
    <% } %>
    <% if (ctx.postMetrics.length) { %>
        <ul class='compact-post-metrics'><!--
        --><% for (let pm of ctx.postMetrics) { %><!--
                --><li><!--
                    --><a href="<%- ctx.formatClientLink('tag', pm.tag_name) %>"
                          class="<%= ctx.makeCssName(pm.tag.category, 'tag') %>"><!--
                        --><i class='fas fa-drafting-compass'></i><!--
                    --><%- pm.tag_name %>: <%- pm.value %></a><!--
                --></li><!--
            --><% } %><!--
        --></ul>
    <% } %>
</div>
