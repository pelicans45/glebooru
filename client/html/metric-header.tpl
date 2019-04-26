<form class='horizontal'>
    <ul class='metric-list'></ul>
    <%= ctx.makeCheckbox({
        text: 'Show values on posts',
        name: 'show-values-on-posts',
        checked: ctx.showValuesOnPost,
        class: 'append'}) %>
    <a href class='mousetrap button append close'>Start sorting</a>
</form>
