<div class='pool-list table-wrap'>
    <% if (ctx.response.results.length) { %>
        <table>
            <thead>
                <th class='names'>
                    <% if (ctx.parameters.q == 'sort:name' || !ctx.parameters.q) { %>
                        <a href='<%- ctx.formatClientLink('pools', {q: '-sort:name'}) %>'>Pool name</a>
                    <% } else { %>
                        <a href='<%- ctx.formatClientLink('pools', {q: 'sort:name'}) %>'>Pool name</a>
                    <% } %>
                </th>
                <th class='post-count'>
                     <% if (ctx.parameters.q == 'sort:post-count') { %>
                        <a href='<%- ctx.formatClientLink('pools', {q: '-sort:post-count'}) %>'>Post count</a>
                     <% } else { %>
                        <a href='<%- ctx.formatClientLink('pools', {q: 'sort:post-count'}) %>'>Post count</a>
                     <% } %>
                     </th>
                <th class='creation-time'>
                    <% if (ctx.parameters.q == 'sort:creation-time') { %>
                        <a href='<%- ctx.formatClientLink('pools', {q: '-sort:creation-time'}) %>'>Created</a>
                    <% } else { %>
                        <a href='<%- ctx.formatClientLink('pools', {q: 'sort:creation-time'}) %>'>Created</a>
                    <% } %>
                </th>
            </thead>
            <tbody>
                <% for (let pool of ctx.response.results) { %>
                    <tr>
                        <td class='names'>
                            <ul>
                                <% for (let name of pool.names) { %>
                                    <li><%= ctx.makePoolLink(pool.id, false, false, pool, name) %></li>
                                <% } %>
                            </ul>
                        </td>
                        <td class='post-count'>
                            <a href='<%- ctx.formatPostsLink({q: 'pool:' + pool.id}) %>'><%- pool.postCount %></a>
                        </td>
                        <td class='creation-time'>
                            <%= ctx.makeRelativeTime(pool.creationTime) %>
                        </td>
                    </tr>
                <% } %>
            </tbody>
        </table>
    <% } %>
</div>
