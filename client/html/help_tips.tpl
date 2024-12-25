<ul>
<!-- <li><a href="/register">Register</a> an account to upload and tag images</a></li> -->
<!-- <li>A privileged account is required to upload and tag images - <a href="/register">register</a> an account and join our <a target="_blank" href="/discord/">Discord</a> to request privileges</li> -->
<li>Download images by shift-clicking (gallery thumbnails or full images), pressing <code>S</code> on an image page, or clicking the download button at the top right of the image page</li>
<li>
When viewing an image:
    <ul>
    <li>Click the previous/next buttons, press the left/right arrow keys (or <code>A</code> and <code>D</code>), or swipe left/right on mobile to view neighboring images</li>
    <li>Click the random image button or press <code>R</code> to view a random image</li>
    <li>If you've searched for tags before clicking the image, these will navigate to other images matched by those tags</li>
    </ul>
</li>
<li>
To add tags when uploading or editing an image:
    <ul>
    <li>Type a tag name and press <code>Space</code> or <code>Enter</code></li>
    <li>Type the start of a tag name and
        <ul>
            <li>Press <code>Tab</code> to select the first suggestion, or</li>
            <li>Use the up/down arrow keys and press <code>Enter</code> to select a suggestion, or</li>
            <li>Click a suggestion</li>
        </ul>
        <li>If the tag doesn't exist, it will be created automatically</li>
    </ul>
</li>
<li style="display: none">A dashed red background around a gallery thumbnail means the image has no tags yet - if you see one, consider adding tags to it</li>
<li>Use underscores to search for tags that contain spaces (<code>"red hair" -> "red_hair"</code>)</li>
<li>Multiple files can be uploaded at once</li>
<% for (const tip of ctx.tips) { %>
<li><%- tip %></li>
<% } %>
</ul>
