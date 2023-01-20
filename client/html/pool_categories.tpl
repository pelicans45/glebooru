<div class='content-wrapper pool-categories'>
    <form>
        <h1>Pool categories</h1>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th class='name'>Category name</th>
                        <th class='color'>Color</th>
                        <th class='usages'>Usages</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </div>

        <% if (ctx.canCreate) { %>
            <p><a class='add'>Add new category</a></p>
        <% } %>

        <div class='messages'></div>

        <% if (ctx.canCreate || ctx.canEditName || ctx.canEditColor || ctx.canDelete) { %>
            <div class='buttons'>
                <input type='submit' class='save' value='Save changes'>
            </div>
        <% } %>
    </form>
</div>
