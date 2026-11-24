
"""COSC 304 Lab 7: List all customer orders."""

from flask import Blueprint, current_app

from db import get_connection
from html_utils import escape_html, format_currency, html_page


# Blueprint must have a unique name
bp = Blueprint("listorder", __name__)


@bp.get("/listorder")
def list_orders():

    connection = None

    try:
        # STEP 1: Connect to SQL Server
        connection = get_connection()
        cursor = connection.cursor()

        # STEP 2: Retrieve all orders and customer details
        cursor.execute("""
            SELECT
                o.orderId,
                o.orderDate,
                o.totalAmount,
                o.customerId,
                c.firstName,
                c.lastName
            FROM ordersummary AS o
            LEFT JOIN customer AS c
                ON o.customerId = c.customerId
            ORDER BY o.orderId
        """)

        orders = cursor.fetchall()

        # STEP 3: Create HTML output
        html = """
        <h1>List of All Orders</h1>

        <p>
            The following orders have been placed
            in the grocery store.
        </p>
        """

        if not orders:
            html += """
            <p>No orders have been placed yet.</p>
            """

        # STEP 4: Display each order
        for order in orders:

            customer_name = (
                f"{order.firstName or ''} "
                f"{order.lastName or ''}"
            ).strip()

            if not customer_name:
                customer_name = "Unknown Customer"

            html += f"""
            <h2>Order ID: {order.orderId}</h2>

            <p>
                <strong>Customer ID:</strong>
                {order.customerId}
            </p>

            <p>
                <strong>Customer Name:</strong>
                {escape_html(customer_name)}
            </p>

            <p>
                <strong>Order Date:</strong>
                {escape_html(order.orderDate)}
            </p>

            <table>
                <thead>
                    <tr>
                        <th>Product ID</th>
                        <th>Product Name</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>

                <tbody>
            """

            # STEP 5: Retrieve products for this order
            # Use a parameterized SQL query
            cursor.execute("""
                SELECT
                    op.productId,
                    p.productName,
                    op.quantity,
                    op.price
                FROM orderproduct AS op
                JOIN product AS p
                    ON op.productId = p.productId
                WHERE op.orderId = ?
                ORDER BY op.productId
            """, order.orderId)

            products = cursor.fetchall()

            # STEP 6: Display products
            for product in products:

                subtotal = (
                    product.quantity * product.price
                )

                html += f"""
                <tr>
                    <td>{product.productId}</td>

                    <td>
                        {escape_html(product.productName)}
                    </td>

                    <td>{product.quantity}</td>

                    <td>
                        {format_currency(product.price)}
                    </td>

                    <td>
                        {format_currency(subtotal)}
                    </td>
                </tr>
                """

            html += f"""
                </tbody>
                <tfoot>
                    <tr>
                        <th colspan="4">
                            Order Total
                        </th>
                        <th>
                            {format_currency(order.totalAmount)}
                        </th>
                    </tr>
                </tfoot>
            </table>

            <hr>
            """

        # STEP 7: Return completed HTML page
        html += """
        <p>
            <a class="button secondary"
               href="/">
                Back to Main Page
            </a>
        </p>
        """

        return html_page(
            "All Orders",
            html
        )

    except Exception:

        current_app.logger.exception(
            "Unable to retrieve customer orders"
        )

        return html_page(
            "Order List Error",
            """
            <h1>Unable to retrieve orders.</h1>

            <p>
                An error occurred while loading
                the order history.
            </p>

            <p>
                <a href="/">Back to Main Page</a>
            </p>
            """
        ), 500

    finally:
        # STEP 8: Close database connection
        if connection is not None:
            connection.close()
