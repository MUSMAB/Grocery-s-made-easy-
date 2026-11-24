
"""COSC 304 Lab 8: Customer information page."""

from flask import Blueprint, session, current_app

from db import get_connection
from html_utils import escape_html, html_page
from routes.auth import require_login

bp = Blueprint("customer", __name__)


@bp.get("/customer")
def customer_information():

    # Require an authenticated user
    redirect_response = require_login()

    if redirect_response is not None:
        return redirect_response

    # IMPORTANT:
    # Get the username from the authenticated session,
    # NOT from customerId or the URL.
    username = session["authenticatedUser"]

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Parameterized SQL query
        cursor.execute("""
            SELECT
                customerId,
                userid,
                firstName,
                lastName,
                email,
                phonenum,
                address,
                city,
                state,
                postalCode,
                country
            FROM customer
            WHERE userid = ?
        """, username)

        customer = cursor.fetchone()

        # Handle missing customer record
        if customer is None:
            session.pop("authenticatedUser", None)

            return html_page(
                "Customer Not Found",
                """
                <h1>Customer Not Found</h1>
                <p>Your customer account could not be found.</p>
                <p><a href="/login">Return to Login</a></p>
                """
            ), 404

        # Display only the currently logged-in customer
        html = f"""
        <h1>My Customer Information</h1>

        <h2>
            Welcome,
            {escape_html(customer.firstName)}
            {escape_html(customer.lastName)}!
        </h2>

        <table>
            <tr>
                <th>Customer ID</th>
                <td>{escape_html(customer.customerId)}</td>
            </tr>
            <tr>
                <th>User ID</th>
                <td>{escape_html(customer.userid)}</td>
            </tr>
            <tr>
                <th>First Name</th>
                <td>{escape_html(customer.firstName)}</td>
            </tr>
            <tr>
                <th>Last Name</th>
                <td>{escape_html(customer.lastName)}</td>
            </tr>
            <tr>
                <th>Email</th>
                <td>{escape_html(customer.email)}</td>
            </tr>
            <tr>
                <th>Phone Number</th>
                <td>{escape_html(customer.phonenum)}</td>
            </tr>
            <tr>
                <th>Address</th>
                <td>{escape_html(customer.address)}</td>
            </tr>
            <tr>
                <th>City</th>
                <td>{escape_html(customer.city)}</td>
            </tr>
            <tr>
                <th>State / Province</th>
                <td>{escape_html(customer.state)}</td>
            </tr>
            <tr>
                <th>Postal Code</th>
                <td>{escape_html(customer.postalCode)}</td>
            </tr>
            <tr>
                <th>Country</th>
                <td>{escape_html(customer.country)}</td>
            </tr>
        </table>

        <p>
            <a class="button secondary"
               href="/listprod">Continue Shopping</a>

            <a class="button secondary"
               href="/logout">Logout</a>
        </p>
        """

        return html_page("My Customer Information", html)

    except Exception:
        current_app.logger.exception(
            "Unable to retrieve customer information"
        )

        return html_page(
            "Customer Error",
            "<h1>Unable to retrieve customer information.</h1>"
        ), 500

    finally:
        if connection is not None:
            connection.close()
