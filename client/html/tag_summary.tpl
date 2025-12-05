<div class='content-wrapper tag-summary'>
    <section class='details'>
        <section>
            Category:
            <span class='<%= ctx.makeCssName(ctx.tag.category, 'tag') %>'><%- ctx.tag.category %></span>
        </section>

        <section>
        Aliases:<br/>
        <ul><!--
            --><% for (let name of ctx.tag.names.slice(1)) { %><!--
                --><li><%= ctx.makeTagLink(name, false, false, ctx.tag) %></li><!--
            --><% } %><!--
        --></ul>
        </section>

        <section>
        Implications:<br/>
        <ul><!--
            --><% for (let tag of ctx.tag.implications) { %><!--
                --><li><%= ctx.makeTagLink(tag.names[0], false, false, tag) %></li><!--
            --><% } %><!--
        --></ul>
        </section>

        <% if (false) { %>
        <section>
        Suggestions:<br/>
        <ul><!--
            --><% for (let tag of ctx.tag.suggestions) { %><!--
                --><li><%= ctx.makeTagLink(tag.names[0], false, false, tag) %></li><!--
            --><% } %><!--
        --></ul>
        </section>
        <% } %>
    </section>

    <section class='description'>
        <hr/>
        <%= ctx.makeMarkdown(ctx.tag.description || 'This tag has no description yet') %>
        <p>This tag has <a href='<%- "https://jej.lol/" + ctx.escapeTagName(ctx.tag.names[0]) %>'><%- ctx.tag.postCount %> <%= ctx.tag.postCount === 1 ? "usage" : "usages" %></a> across all sub-boorus</p>
    </section>
</div>
