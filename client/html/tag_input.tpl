<div class='tag-input'>
    <div class='main-control'>
        <input type='text' placeholder='<%- ctx.tagsPlaceholder %>'/>
        <button style="display: none">Add</button>
    </div>

    <div class='tag-suggestions'>
        <div class='wrapper'>
            <p>
                <span class='buttons'>
                    <a class='opacity'><i class='la la-eye'></i></a>
                    <a class='close'>×</a>
                </span>
                Suggested tags
            </p>
            <ul></ul>
        </div>
    </div>

    <ul class='compact-tags'></ul>

    <a class='tag-from-lookalikes'>From lookalikes...</a>
</div>
