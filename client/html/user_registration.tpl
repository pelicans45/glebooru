<div class='content-wrapper' id='user-registration'>
    <h1>Register</h1>
    <form autocomplete='off'>
        <input class='anticomplete' type='text' name='fakeuser'/>
        <input class='anticomplete' type='password' name='fakepass'/>

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
                    placeholder: '8+ characters',
                    required: true,
                    pattern: ctx.passwordPattern,
                }) %>
            </li>
            <li style="display: none">
                <%= ctx.makeEmailInput({
                    text: 'Email',
                    name: 'email',
                    placeholder: 'optional',
                }) %>
                <p class='hint'>
                    (Optional) To reset the password, if needed
                </p>
            </li>
        </ul>

        <div class='messages'></div>
        <div class='buttons'>
            <input type='submit' value='Create account'/>
        </div>
    </form>

    <div class='info' style="display: none">
        <p>Registered users can:</p>
        <ul>
            <li><i class='la la-upload'></i> upload new posts</li>
            <li><i class='la la-heart'></i> mark them as favorite</li>
            <li><i class='lar la-comment-dots'></i> add comments</li>
            <li><i class='la la-star-half-alt'></i> vote up/down on posts and comments</li>
        </ul>
        <hr/>
        <p>By creating an account, you are agreeing to the <a href='<%- ctx.formatClientLink('help', 'tos') %>'>Terms of Service</a>.</p>
    </div>
</div>
