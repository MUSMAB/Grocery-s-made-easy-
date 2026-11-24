
"""COSC 304 Lab 8: Validate customer login."""

from flask import (
    Blueprint,
    current_app,
    redirect,
    request,
    session,
    url_for
)

from db import get_connection

bp = Blueprint("validate_login", __name__)


@bp.post("/validateLogin")
def validate_login():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    valid_login = False
    connection = None

    if username and password:

        try:
            connection = get_connection()
            cursor = connection.cursor()

            # Parameterized SQL query
            # The ? placeholders prevent SQL injection.
            cursor.execute("""
                SELECT customerId
                FROM customer
                WHERE userid = ?
                  AND password = ?
            """, username, password)

            user = cursor.fetchone()

            # Successful login only when the user exists
            if user is not None:
                valid_login = True

        except Exception:
            current_app.logger.exception(
                "Unable to validate customer login"
            )

            session.pop("authenticatedUser", None)
            session["loginMessage"] = (
                "Unable to validate login right now."
            )

            return redirect(
                url_for("login.login_page")
            )

        finally:
            if connection is not None:
                connection.close()

    if valid_login:

        # Store the authenticated username in session
        session["authenticatedUser"] = username

        session.pop("loginMessage", None)

        return redirect(url_for("index"))

    # Unsuccessful login
    session.pop("authenticatedUser", None)

    session["loginMessage"] = (
        "Invalid user ID or password."
    )

    return redirect(url_for("login.login_page"))
