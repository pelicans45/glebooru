<div class='tag-list table-wrap'>
    <% if (ctx.response.results.length) { %>
        <table>
            <thead>
                <th class='names'>
                    <% if (ctx.parameters.q == 'sort:name' || !ctx.parameters.q) { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: '-sort:name'}) %>'>Tag name</a>
                    <% } else { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: 'sort:name'}) %>'>Tag name</a>
                    <% } %>
                </th>
                <th class='implications'>
                    <% if (ctx.parameters.q == 'sort:implication-count') { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: '-sort:implication-count'}) %>'>Implications</a>
                    <% } else { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: 'sort:implication-count'}) %>'>Implications</a>
                    <% } %>
                </th>
                <th class='suggestions'>
                    <% if (ctx.parameters.q == 'sort:suggestion-count') { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: '-sort:suggestion-count'}) %>'>Suggestions</a>
                    <% } else { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: 'sort:suggestion-count'}) %>'>Suggestions</a>
                    <% } %>
                </th>
                <th class='usages'>
                    <% if (ctx.parameters.q == 'sort:usages') { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: '-sort:usages'}) %>'>Usages</a>
                    <% } else { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: 'sort:usages'}) %>'>Usages</a>
                    <% } %>
                </th>
                <th class='creation-time'>
                    <% if (ctx.parameters.q == 'sort:creation-time') { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: '-sort:creation-time'}) %>'>Created</a>
                    <% } else { %>
                        <a href='<%- ctx.formatClientLink('tags', {q: 'sort:creation-time'}) %>'>Created</a>
                    <% } %>
                </th>
            </thead>
            <tbody>
                <% for (let tag of ctx.response.results) {
                    if (ctx.hostnameExcludedTag(tag)) {
                        continue;
                    }
                %>
                    <tr>
                        <td class='names'>
                            <ul>
                                <% for (let name of tag.names) { %>
                                    <li><%= ctx.makeTagLink(name, false, false, tag) %></a></li>
                                <% } %>
                            </ul>
                            <span class='tag-page-search'><a href='<%- ctx.formatPostsLink({q: ctx.escapeTagName(tag.names[0])}) %>'><i class="la la-search"></i></a></span>
                        </td>
                        <td class='implications'>
                            <% if (tag.implications.length) { %>
                                <ul>
                                    <% for (let relation of tag.implications) { %>
                                        <li><%= ctx.makeTagLink(relation.names[0], false, false, relation) %></li>
                                    <% } %>
                                </ul>
                            <% } else { %>
                                -
                            <% } %>
                        </td>
                        <td class='suggestions'>
                            <% if (tag.suggestions.length) { %>
                                <ul>
                                    <% for (let relation of tag.suggestions) { %>
                                        <li><%= ctx.makeTagLink(relation.names[0], false, false, relation) %></li>
                                    <% } %>
                                </ul>
                            <% } else { %>
                                -
                            <% } %>
                        </td>
                        <td class='usages'>
                            <a href='<%- ctx.formatClientLink('posts', {q: tag.names[0]}) %>'><%- tag.postCount %></a>
                        </td>
                        <td class='creation-time'>
                            <%= ctx.makeRelativeTime(tag.creationTime) %>
                        </td>
                    </tr>
                <% } %>
            </tbody>
        </table>
    <% } %>
</div>
