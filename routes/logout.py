
"""COSC 304 Lab 8: Customer logout."""

from flask import Blueprint, redirect, session, url_for

bp = Blueprint("logout", __name__)


@bp.get("/logout")
def log_out():

    # Clear current Lab 8 login
    session.pop("authenticatedUser", None)
    session.pop("loginMessage", None)

    # Clear possible login variables from older code
    session.pop("logged_in_user", None)
    session.pop("login_userid", None)

    # Keep shopping cart unchanged
    return redirect(url_for("index"))
