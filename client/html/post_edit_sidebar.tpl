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

        <% if (ctx.canEditPostTags) { %>
            <section class='tags'>
                <%= ctx.makeTextInput({}) %>
            </section>
        <% } %>

        <% if (ctx.canEditPostRelations) { %>
            <section class='relations'>
                <%= ctx.makeTextInput({
                    text: 'Relations',
                    name: 'relations',
                    placeholder: 'space- or comma-separated post IDs',
                    pattern: '^[0-9 ,]*$',
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
                <%= ctx.makeTextarea({
                    text: 'Source',
                    value: ctx.post.source,
                }) %>
            </section>
        <% } %>

        <% if (ctx.canEditPoolPosts) { %>
            <section class='pools'>
                <%= ctx.makeTextInput({}) %>
            </section>
        <% } %>

        <% /* if (ctx.canEditPostMetrics) { %>
            <section class='metrics'>
                <%= ctx.makeTextInput({}) %>
            </section>
        <% } */ %>

        <% if (ctx.canEditPostNotes) { %>
            <section class='notes'>
                <a class='add'>Add a note</a>
                <%= ctx.makeTextarea({disabled: true, text: 'Content (supports Markdown)', rows: '8'}) %>
                <a class='delete inactive'>Delete selected note</a>
                <% if (ctx.hasClipboard) { %>
                    <br/>
                    <a class='copy'>Export notes to clipboard</a>
                    <br/>
                    <a class='paste'>Import notes from clipboard</a>
                <% } %>
            </section>
        <% } %>

        <% if (ctx.canEditPostContent) { %>
            <section class='post-content'>
                <label>Content</label>
                <div class='dropper-container'></div>
            </section>
        <% } %>

        <% // Thumbnail editing disabled %>
        <% if (false && ctx.canEditPostThumbnail) { %>
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
                        <li><a class='feature' style='display: none'>Feature this post on main page</a></li>
                    <% } %>
                    <% if (ctx.canMergePosts) { %>
                        <li><a class='merge'>Merge this post with another</a></li>
                    <% } %>
                    <% if (ctx.canDeletePosts) { %>
                        <li><a class='delete'>Delete this post</a></li>
                    <% } %>
                </ul>
            </section>
        <% } %>
    </form>
</div>
