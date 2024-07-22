<div id='post-upload'>
    <form>
        <div class='dropper-container'></div>

        <div class='control-strip'>
            <input type='submit' value='Upload' class='submit'/>

            <span class='skip-duplicates control-checkbox' style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Skip duplicate',
                    name: 'skip-duplicates',
                    checked: false,
                }) %>
            </span>

            <span class='copy-tags-to-originals control-checkbox' style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Copy tags to originals',
                    name: 'copy-tags-to-originals',
                    checked: false,
                }) %>
            </span>

            <span class='always-upload-similar' style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Force upload similar',
                    name: 'always-upload-similar',
                    checked: false,
                }) %>
            </span>

            <span class='pause-remain-on-error' style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Pause on error',
                    name: 'pause-remain-on-error',
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
