<div id='post-upload'>
    <form>
        <div class='dropper-container'></div>

        <div class='control-strip'>
            <input type='submit' value='Upload all' class='submit'/>

            <span class='skip-duplicates control-checkbox'>
                <%= ctx.makeCheckbox({
                    text: 'Skip duplicate',
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

            <span class='always-upload-similar'>
                <%= ctx.makeCheckbox({
                    text: 'Force upload similar',
                    name: 'always-upload-similar',
                    checked: false,
                }) %>
            </span>

            <div class='tags'>
                <%= ctx.makeTextInput({}) %>
            </div>

            <span class='pause-remain-on-error'>
                <%= ctx.makeCheckbox({
                    text: 'Pause on error',
                    name: 'pause-remain-on-error',
                    checked: true,
                }) %>
            </span>

            <%= ctx.makeTextInput({placeholder: 'Common tags', id: 'common-tags', name: 'common-tags', style: 'margin-top:1em;'}) %>

            <input type='button' value='Cancel' class='cancel'/>
        </div>

        <div class='messages'></div>

        <ul class='uploadables-container'></ul>
    </form>
</div>
