<div class='edit-sidebar'>
    <form autocomplete='off'>
        <input type='submit' value='Save' class='submit'/>

        <div class='messages'></div>

        <% if (ctx.enableSafety && ctx.canEditPostSafety) { %>
            <section class='safety'>
                <label>Safety</label>
                <div class='radio-wrapper'>
                    <%= ctx.makeRadio({
                        name: 'safety',
                        class: 'safety-safe',
                        value: 'safe',
                        selectedValue: ctx.post.safety,
                        text: 'Safe'}) %>
                    <%= ctx.makeRadio({
                        name: 'safety',
                        class: 'safety-sketchy',
                        value: 'sketchy',
                        selectedValue: ctx.post.safety,
                        text: 'Sketchy'}) %>
                    <%= ctx.makeRadio({
                        name: 'safety',
                        value: 'unsafe',
                        selectedValue: ctx.post.safety,
                        class: 'safety-unsafe',
                        text: 'Unsafe'}) %>
                </div>
            </section>
        <% } %>

        <% if (ctx.canEditPostRelations) { %>
            <section class='relations'>
                <%= ctx.makeTextInput({
                    text: 'Relations',
                    name: 'relations',
                    placeholder: 'space-separated post IDs',
                    pattern: '^[0-9 ]*$',
                    value: ctx.post.relations.map(rel => rel.id).join(' '),
                }) %>
            </section>
        <% } %>

        <% if (ctx.canEditPostFlags && ctx.post.type === 'video') { %>
            <section class='flags'>
                <label>Miscellaneous</label>
                <%= ctx.makeCheckbox({
                    text: 'Loop video',
                    name: 'loop',
                    checked: ctx.post.flags.includes('loop'),
                }) %>
                <%= ctx.makeCheckbox({
                    text: 'Sound',
                    name: 'sound',
                    checked: ctx.post.flags.includes('sound'),
                }) %>
            </section>
        <% } %>

        <% if (ctx.canEditPostSource) { %>
            <section class='post-source'>
                <%= ctx.makeTextInput({
                    text: 'Source',
                    name: 'source',
                    value: ctx.post.source,
                }) %>
            </section>
        <% } %>

        <% if (ctx.canEditPostTags) { %>
            <section class='tags'>
                <%= ctx.makeTextInput({}) %>
            </section>
        <% } %>

        <% if (ctx.canEditPostMetrics) { %>
        <section class='metrics'>
            <% if (ctx.post.tags.filterMetrics().length) { %>
                <ul class='compact-unset-metrics'><!--
                    --><% for (let tag of ctx.post.tags.filterMetrics()) { %><!--
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
                        --></li><!--
                    --><% } %><!--
                --></ul>
                <% if (ctx.post.metrics.length) { %><hr><% } %>
            <% } %>
            <% if (ctx.post.metrics.length) { %>
                <ul class='compact-post-metrics'><!--
                --><% for (let pm of ctx.post.metrics) { %><!--
                        --><li><!--
                            --><a href="<%- ctx.formatClientLink('tag', pm.tag_name) %>"
                                    class="<%= ctx.makeCssName(pm.tag.category, 'tag') %>"><!--
                                --><i class='fas fa-drafting-compass'></i><!--
                            --><%- pm.tag_name %>: <%- pm.value %></a><!--
                        --></li><!--
                    --><% } %><!--
                --></ul>
            <% } %>
        </section>
        <% } %>

        <% if (ctx.canEditPostNotes) { %>
            <section class='notes'>
                <a href class='add'>Add a note</a>
                <%= ctx.makeTextarea({disabled: true, text: 'Content (supports Markdown)', rows: '8'}) %>
                <a href class='delete inactive'>Delete selected note</a>
                <% if (ctx.hasClipboard) { %>
                    <br/>
                    <a href class='copy'>Export notes to clipboard</a>
                    <br/>
                    <a href class='paste'>Import notes from clipboard</a>
                <% } %>
            </section>
        <% } %>

        <% if (ctx.canEditPostContent) { %>
            <section class='post-content'>
                <label>Content</label>
                <div class='dropper-container'></div>
            </section>
        <% } %>

        <% if (ctx.canEditPostThumbnail) { %>
            <section class='post-thumbnail'>
                <label>Thumbnail</label>
                <div class='dropper-container'></div>
                <a href>Discard custom thumbnail</a>
            </section>
        <% } %>

        <% if (ctx.canFeaturePosts || ctx.canDeletePosts || ctx.canMergePosts) { %>
            <section class='management'>
                <ul>
                    <% if (ctx.canFeaturePosts) { %>
                        <li><a href class='feature'>Feature this post on main page</a></li>
                    <% } %>
                    <% if (ctx.canMergePosts) { %>
                        <li><a href class='merge'>Merge this post with another</a></li>
                    <% } %>
                    <% if (ctx.canDeletePosts) { %>
                        <li><a href class='delete'>Delete this post</a></li>
                    <% } %>
                </ul>
            </section>
        <% } %>
    </form>
</div>
