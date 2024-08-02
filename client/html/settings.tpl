<div class='content-wrapper' id='settings'>
    <form onsubmit="setTimeout(() => location.reload(), 600)">
        <strong style="font-size: 110%">Settings</strong>
        <p style="display: none">(These settings only apply to your browser.)</p>
        <ul class='input'>
            <li style="display: none">
                <%= ctx.makeCheckbox({
                    text: "Enable keyboard shortcuts <a class='append icon' href='" + ctx.formatClientLink('help', 'keyboard') + "'><i class='la la-question-circle-o'></i></a>",
                    name: 'keyboard-shortcuts',
                    checked: ctx.browsingSettings.keyboardShortcuts,
                }) %>
            </li>

            <li class='uploadSafety' style="display: none">
                <label>Safety</label>
                <div class='radio-wrapper'>
                    <%= ctx.makeRadio({
                    name: 'safety',
                    class: 'safety-safe',
                    value: 'safe',
                    selectedValue: ctx.browsingSettings.uploadSafety,
                    text: 'Safe'}) %>
                    <%= ctx.makeRadio({
                    name: 'safety',
                    class: 'safety-sketchy',
                    value: 'sketchy',
                    selectedValue: ctx.browsingSettings.uploadSafety,
                    text: 'Sketchy'}) %>
                    <%= ctx.makeRadio({
                    name: 'safety',
                    value: 'unsafe',
                    selectedValue: ctx.browsingSettings.uploadSafety,
                    class: 'safety-unsafe',
                    text: 'Unsafe'}) %>
                </div>
            </li>

            <li>
            <li style="display: none">
                <%= ctx.makeNumericInput({
                    text: 'Number of posts per page',
                    name: 'posts-per-page',
                    checked: ctx.browsingSettings.postCount,
                    value: ctx.browsingSettings.postsPerPage,
                    min: 10,
                    max: 100,
                }) %>
            </li>

            <li style="display: none">
                <%= ctx.makeNumericInput({
                text: 'Number of similar posts',
                name: 'similar-posts',
                value: ctx.browsingSettings.similarPosts,
                min: 0,
                max: 100,
                }) %>
            </li>

            <li style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Upscale small posts',
                    name: 'upscale-small-posts',
                    checked: ctx.browsingSettings.upscaleSmallPosts}) %>
            </li>

            <li style='display: none'>
                <%= ctx.makeCheckbox({
                    text: 'Dark theme',
                    name: 'dark-theme',
                    checked: ctx.browsingSettings.darkTheme,
                    title: 'Enable dark theme',
                }) %>
            </li>

            <li>
                <%= ctx.makeCheckbox({
                    text: 'Endless scroll',
                    name: 'endless-scroll',
                    checked: ctx.browsingSettings.endlessScroll,
                    title: 'Load gallery pages automatically when scrolling',
                }) %>
            </li>

            <li>
                <%= ctx.makeCheckbox({
                    text: 'Sticky navigation bar',
                    name: 'navbar-follow',
                    checked: ctx.browsingSettings.navbarFollow,
                    title: 'Keep the navigation bar at the top of the screen when scrolling down',
                }) %>
            </li>

            <li class='layoutType'>
                <label>Gallery Layout</label>
                <div class='radio-wrapper'>
                    <%= ctx.makeRadio({
                    name: 'layout-type',
                    value: 'default',
                    selectedValue: ctx.browsingSettings.layoutType,
                    text: 'Default'}) %>
                    <%= ctx.makeRadio({
                    name: 'layout-type',
                    value: 'grid',
                    selectedValue: ctx.browsingSettings.layoutType,
                    text: 'Grid'}) %>
                    <%= ctx.makeRadio({
                    name: 'layout-type',
                    value: 'column',
                    selectedValue: ctx.browsingSettings.layoutType,
                    text: 'Column'}) %>
                </div>
            </li>

            <li style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Use post flow',
                    name: 'post-flow',
                    checked: ctx.browsingSettings.postFlow,
                }) %>
                <p class='hint'>Use a content-aware flow for thumbnails on the post search page.</p>
            </li>

            <li style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Enable transparency grid',
                    name: 'transparency-grid',
                    checked: ctx.browsingSettings.transparencyGrid,
                }) %>
                <p class='hint'>Renders a checkered pattern behind posts with transparent background.</p>
            </li>

            <li style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Show tag suggestions',
                    name: 'tag-suggestions',
                    checked: ctx.browsingSettings.tagSuggestions,
                }) %>
                <p class='hint'>Shows a popup with suggested tags in edit forms.</p>
            </li>

            <li style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Automatically play video posts',
                    name: 'autoplay-videos',
                    checked: ctx.browsingSettings.autoplayVideos,
                }) %>
            </li>

            <li style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Display underscores as spaces',
                    name: 'underscores-as-spaces',
                    checked: ctx.browsingSettings.tagUnderscoresAsSpaces,
                }) %>
                <p class='hint'>Display all underscores as if they were spaces. This is only a visual change, which means that you'll still have to use underscores when searching or editing tags.</p>
            </li>
        </ul>

        <div class='messages'></div>
        <div class='buttons'>
            <input type='submit' value='Save settings'/>
        </div>
    </form>
</div>
