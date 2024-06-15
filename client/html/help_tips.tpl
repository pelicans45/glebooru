<ul>
<li>Download images by shift-clicking (gallery thumbnails or full images), pressing <code>S</code> on an image page, or clicking the download button</li>
<li>
When viewing an image:
    <ul>
    <li>Click the arrow buttons, press the arrow keys (or <code>A</code> and <code>D</code>), or swipe on mobile to view neighboring images</li>
    <li>Click the random image button or press <code>R</code> to view a random image</li>
    <li>If you've searched for tags, these will navigate to other images matched by those tags</li>
    </ul>
</li>
<li>The upload page supports folders and multiple files</li>
<li>Use underscores when searching for tags containing spaces ("<code>concept art</code>" -> "<code>concept_art</code>")</li>
<% for (const tip of ctx.tips) { %>
<li><%- tip %></li>
<% } %>
</ul>
