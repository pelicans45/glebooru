<div class='tag-delete'>
    <form>
        <p>This tag has <a href='<%- ctx.formatPostsLink({q: ctx.escapeTagName(ctx.tag.names[0])}) %>'><%- ctx.tag.postCount %> <%= ctx.tag.postCount === 1 ? "usage" : "usages" %></a>.</p>

        <ul class='input'>
            <li>
                <%= ctx.makeCheckbox({
                    name: 'confirm-deletion',
                    text: 'I confirm that I want to delete this tag',
                    required: true,
                }) %>
            </li>
        </ul>

        <div class='messages'></div>

        <div class='buttons'>
            <input type='submit' value='Delete tag'/>
        </div>
    </form>
</div>
