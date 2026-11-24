
"""COSC 304 Lab 8: Administrator daily sales report."""

from flask import Blueprint, current_app

from db import get_connection
from html_utils import escape_html, format_currency, html_page
from routes.auth import require_login

bp = Blueprint("admin", __name__)


@bp.get("/admin")
def admin_report():

    # STEP 1: Require login
    redirect_response = require_login()

    if redirect_response is not None:
        return redirect_response

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # STEP 2: Calculate total sales for each day
        cursor.execute("""
            SELECT
                CAST(orderDate AS DATE) AS salesDate,
                SUM(totalAmount) AS dailyTotal
            FROM ordersummary
            GROUP BY CAST(orderDate AS DATE)
            ORDER BY salesDate ASC
        """)

        sales = cursor.fetchall()

        # STEP 3: Build daily sales report
        html = """
        <h1>Administrator Sales Report by Day</h1>

        <p>Total sales grouped by order date.</p>

        <table>
            <thead>
                <tr>
                    <th>Order Date</th>
                    <th>Total Order Amount</th>
                </tr>
            </thead>

            <tbody>
        """

        if not sales:
            html += """
            <tr>
                <td colspan="2">No sales found.</td>
            </tr>
            """

        for row in sales:

            html += f"""
            <tr>
                <td>{escape_html(row.salesDate)}</td>
                <td>{format_currency(row.dailyTotal)}</td>
            </tr>
            """

        html += """
            </tbody>
        </table>

        <p>
            <a href="/">Back to Main Page</a>
        </p>

        <p>
            <a href="/logout">Logout</a>
        </p>
        """

        return html_page(
            "Administrator Sales Report",
            html
        )

    except Exception:

        current_app.logger.exception(
            "Unable to retrieve administrator sales report"
        )

        return html_page(
            "Sales Report Error",
            "<h1>Unable to retrieve sales report.</h1>"
        ), 500

    finally:
        if connection is not None:
            connection.close()


