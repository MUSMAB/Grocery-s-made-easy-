
"""COSC 304 Lab 8: Shared login protection."""

from flask import redirect, session, url_for


def require_login():
    """
    Redirect to login if the user is not authenticated.
    Return None when the user is already logged in.
    """

    if session.get("authenticatedUser") is None:

        session["loginMessage"] = (
            "Please log in to access that page."
        )

        return redirect(
            url_for("login.login_page")
        )

    return None
