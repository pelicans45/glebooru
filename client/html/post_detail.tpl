<div class='content-wrapper' id='post'>
    <h1>#<%- ctx.post.id %></h1>
    <nav class='buttons'><!--
        --><ul><!--
            --><li><a href='<%- ctx.formatClientLink('', ctx.post.id) %>'><i class='la la-reply'></i> Main view</a></li><!--
            --><% if (ctx.canMerge) { %><!--
                --><li data-name='merge'><a href='<%- ctx.formatClientLink('', ctx.post.id, 'merge') %>'>Merge with&hellip;</a></li><!--
            --><% } %><!--
        --></ul><!--
    --></nav>
    <div class='post-content-holder'></div>
</div>
