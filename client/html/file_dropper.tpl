<div class='file-dropper-holder'>
    <input type='file' id='<%- ctx.id %>' accept='image/*,video/*,audio/*'/>
    <label class='file-dropper' for='<%- ctx.id %>' role='button'>
        Click, drop, or paste
        <% if (ctx.extraText) { %>
            <br/>
            <small><%= ctx.extraText %></small>
        <% } %>
    </label>
    <% if (ctx.allowUrls) { %>
        <div class='url-holder' style='display: none'>
            <input type='text' name='url' placeholder='<%- ctx.urlPlaceholder %>'/>
            <% if (ctx.lock) { %>
                <button>Confirm</button>
            <% } else { %>
                <button>Add</button>
            <% } %>
        </div>
    <% } %>
</div>
