<div class='post-content post-type-<%- ctx.post.type %>'>
    <% if (['image', 'animation'].includes(ctx.post.type)) {
    %>
        <img class='main-content resize-listener' onload="loadMainContentTaggedUrl()" alt='' src='<%- ctx.post.contentUrl %>' draggable='false' fetchpriority='high'/>

    <% /* } else if (ctx.post.type === 'flash') { %>

        <object class='main-content resize-listener' width='<%- ctx.post.canvasWidth %>' height='<%- ctx.post.canvasHeight %>' data='<%- ctx.post.contentUrl %>'>
            <param name='wmode' value='opaque'/>
            <param name='movie' value='<%- ctx.post.contentUrl %>'/>
        </object>

    <% */ } else if (ctx.post.type === 'video') { %>

        <%= ctx.makeElement(
            'video', {
                class: 'main-content resize-listener',
                controls: true,
                loop: (ctx.post.flags || []).includes('loop'),
                playsinline: true,
                autoplay: ctx.autoplay,
            },
            ctx.makeElement('source', {
                type: ctx.post.mimeType,
                src: ctx.post.taggedEnrichedContentUrl,
            }),
            'Your browser doesn\'t support HTML5 videos')
        %>

    <% } else if (ctx.post.type === 'audio') { %>

        <%= ctx.makeElement(
            'audio', {
                class: 'main-content resize-listener',
                controls: true,
                loop: (ctx.post.flags || []).includes('loop'),
                playsinline: true,
                autoplay: ctx.autoplay,
            },
            ctx.makeElement('source', {
                type: ctx.post.mimeType,
                src: ctx.post.taggedEnrichedContentUrl,
            }),
            'Your browser doesn\'t support HTML5 audio')
        %>

    <% } else { console.error('Unknown post type:', ctx.post); } %>

    <div class='post-overlay resize-listener'>
    </div>
</div>
