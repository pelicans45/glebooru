<div class='content-wrapper' id='login'>
    <h1 style="margin-bottom: 0.3em">Login</h1>
    <div style="margin-bottom: 1.3em"><a href="/register">Or click here to register</a></div>
    <form>
        <ul class='input'>
            <li>
                <%= ctx.makeTextInput({
                    text: 'Username',
                    name: 'name',
                    required: true,
                    pattern: ctx.userNamePattern,
                }) %>
            </li>
            <li>
                <%= ctx.makePasswordInput({
                    text: 'Password',
                    name: 'password',
                    required: true,
                    pattern: ctx.passwordPattern,
                }) %>
            </li>
            <li style="display: none">
                <%= ctx.makeCheckbox({
                    text: 'Remember me',
                    name: 'remember-user',
                    checked: true,
                }) %>
            </li>
        </ul>

        <div class='messages'></div>

        <div class='buttons'>
            <input type='submit' value='Login'/>
            <a class='append password-reset' href='<%- ctx.formatClientLink('password-reset') %>'>Forgot password?</a>
        </div>
    </form>
</div>
