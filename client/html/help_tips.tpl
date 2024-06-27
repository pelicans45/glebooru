<ul>
<li>Download images by shift-clicking (gallery thumbnails or full images), pressing <code>S</code> on an image page, or clicking the download button</li>
<li>
When viewing an image:
    <ul>
    <li>Click the previous/next buttons, press the left/right arrow keys (or <code>A</code> and <code>D</code>), or swipe on mobile to view neighboring images</li>
    <li>Click the random image button or press <code>R</code> to view a random image</li>
    <li>If you've searched for tags before clicking the image, these will navigate to other images matched by those tags</li>
    </ul>
</li>
<li>An account is required to upload images and add tags - to request an account, join our <a href="/discord">Discord</a></li>
<li>A dashed red background around a thumbnail means the image has no tags yet - if you see one, consider adding tags to it</li>
<li>The upload page supports folders and multiple files</li>
<li>Use underscores when searching for tags containing spaces ("<code>concept art</code>" -> "<code>concept_art</code>")</li>
<% for (const tip of ctx.tips) { %>
<li><%- tip %></li>
<% } %>
</ul>
