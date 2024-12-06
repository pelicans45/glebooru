<div class='post-content post-type-<%- ctx.post.type %>'>
    <% if (['image', 'animation'].includes(ctx.post.type)) {
        const img = document.createElement("img");
        img.className = "main-content resize-listener";
        img.setAttribute("draggable", "false");
        img.setAttribute("fetchPriority", "high");
        img.addEventListener("load", () => {
            //const taggedUrl = ctx.post.taggedEnrichedContentUrl;
            img.src = ctx.post.taggedEnrichedContentUrl;
            /*
            const tagImg = new Image();
            tagImg.addEventListener("load", () => {
                img.src = taggedUrl;
            })
            tagImg.src = taggedUrl;
            */
        })
        img.src = ctx.post.contentUrl;
    %>
        <%- img.outerHTML %>

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
                src: ctx.post.contentUrl,
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
                src: ctx.post.contentUrl,
            }),
            'Your browser doesn\'t support HTML5 audio')
        %>

    <% } else { console.error('Unknown post type:', ctx.post); } %>

    <div class='post-overlay resize-listener'>
    </div>
</div>
