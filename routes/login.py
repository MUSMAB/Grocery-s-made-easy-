"""COSC 304 Lab 8: Login form."""

from flask import Blueprint, session, url_for
from html_utils import escape_html, html_page

bp = Blueprint("login", __name__)


@bp.get("/login")
def login_page():

    # Display a message after an unsuccessful login
    message = session.pop("loginMessage", None)

    notice = (
        f"<p>{escape_html(message)}</p>"
        if message
        else ""
    )

    html = f"""
    <h1>Store Login</h1>

    <p>Enter your user ID and password to log in.</p>

    {notice}

    <form
        method="post"
        action="{url_for('validate_login.validate_login')}"
    >

        <p>
            <label for="username">User ID:</label>
            <input
                type="text"
                id="username"
                name="username"
                maxlength="20"
                required
            >
        </p>

        <p>
            <label for="password">Password:</label>
            <input
                type="password"
                id="password"
                name="password"
                maxlength="30"
                required
            >
        </p>

        <button type="submit">Log In</button>

    </form>

    <p><a href="/">Back to Main Page</a></p>
    """

    return html_page("Store Login", html)
