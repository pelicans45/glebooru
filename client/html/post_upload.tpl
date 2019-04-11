<div id='post-upload'>
    <form>
        <div class='dropper-container'></div>

        <div class='control-strip'>
            <input type='submit' value='Upload all' class='submit'/>

            <span class='skip-duplicates control-checkbox'>
                <%= ctx.makeCheckbox({
                    text: 'Skip duplicates',
                    name: 'skip-duplicates',
                    checked: false,
                }) %>
            </span>

            <span class='copy-tags-to-originals control-checkbox'>
                <%= ctx.makeCheckbox({
                    text: 'Copy tags to originals',
                    name: 'copy-tags-to-originals',
                    checked: false,
                }) %>
            </span>

            <div class='tags'>
                <%= ctx.makeTextInput({}) %>
            </div>

            <input type='button' value='Cancel' class='cancel'/>
        </div>

        <div class='messages'></div>

        <ul class='uploadables-container'></ul>
    </form>
</div>
