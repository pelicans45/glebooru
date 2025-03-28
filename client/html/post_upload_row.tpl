<li class='uploadable-container'>
    <div class='thumbnail-wrapper'>
        <% if (['image'].includes(ctx.uploadable.type)) { %>

            <a href='<%= ctx.uploadable.previewUrl %>'>
                <%= ctx.makeThumbnail(ctx.uploadable.previewUrl) %>
            </a>

        <% } else if (['video'].includes(ctx.uploadable.type)) { %>

            <div class='thumbnail'>
                <a href='<%= ctx.uploadable.previewUrl %>'>
                    <video id='video' nocontrols muted>
                        <source type='<%- ctx.uploadable.mimeType %>' src='<%- ctx.uploadable.previewUrl %>'/>
                    </video>
                </a>
            </div>

        <% } else if (['audio'].includes(ctx.uploadable.type)) { %>

            <div class='thumbnail'>
                <a href='<%= ctx.uploadable.previewUrl %>'>
                    <audio id='audio' nocontrols>
                        <source type='<%- ctx.uploadable.mimeType %>' src='<%- ctx.uploadable.previewUrl %>'/>
                    </video>
                </a>
            </div>

        <% } else { %>

            <%= ctx.makeThumbnail(null) %>

        <% } %>
    </div>

    <div class='uploadable'>
        <header>
            <nav>
                <ul>
                    <li><a class='move-up'><i class='la la-chevron-up'></i></a></li>
                    <li><a class='move-down'><i class='la la-chevron-down'></i></a></li>
                </ul>
            </nav>
            <nav>
                <ul>
                    <li><a class='remove'><i class='la la-times'></i></a></li>
                </ul>
            </nav>

            <span class='filename'><%= ctx.uploadable.name %></span>
        </header>

        <div class='body'>
            <% if (ctx.enableSafety) { %>
                <div class='safety'>
                    <% for (let safety of ['safe', 'sketchy', 'unsafe']) { %>
                        <%= ctx.makeRadio({
                            name: 'safety-' + ctx.uploadable.key,
                            value: safety,
                            text: safety[0].toUpperCase() + safety.substr(1),
                            selectedValue: ctx.uploadable.safety,
                        }) %>
                    <% } %>
                </div>
            <% } %>

            <div class='options' style="display: none">
                <% if (ctx.canUploadAnonymously) { %>
                    <div class='anonymous'>
                        <%= ctx.makeCheckbox({
                            text: 'Upload anonymously',
                            name: 'anonymous',
                            checked: ctx.uploadable.anonymous,
                            readonly: ctx.uploadable.forceAnonymous,
                        }) %>
                    </div>
                <% } %>
            </div>

            <div class='messages'></div>

            <% if (ctx.uploadable.lookalikes.length) { %>
                <ul class='lookalikes'>
                    <% for (let lookalike of ctx.uploadable.lookalikes) { %>
                        <li>
                            <a class='thumbnail-wrapper' title='@<%- lookalike.post.id %>'
                                href='<%= ctx.canViewPosts ? ctx.getPostUrl(lookalike.post.id) : "" %>'>
                                <%= ctx.makeThumbnail(lookalike.post.thumbnailUrl) %>
                            </a>
                            <div class='description'>
                                Similar post: <%= ctx.makeNewTabPostLink(lookalike.post.id, true) %>
                                <br/>
                                <%- Math.round((1-lookalike.distance) * 100) %>% match
                            </div>
                            <div class='controls'>
                                <% if (lookalike.distance > 0) { %>
                                    <%= ctx.makeCheckbox({text: 'Copy tags', name: 'copy-tags'}) %>
                                    <br/>
                                    <%= ctx.makeCheckbox({text: 'Add relation', name: 'add-relation'}) %>
                                <% } else { %>
                                    <span style="display:none">
                                    <%= ctx.makeCheckbox({text: 'Copy tags', name: 'copy-tags'}) %>
                                    </span>
                                <% } %>
                            </div>
                        </li>
                    <% } %>
                </ul>
            <% } %>
        </div>
    </div>
</li>
