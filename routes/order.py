
"""Question 2 (20 marks): validate and save a completed order."""

from flask import Blueprint, request, session, current_app
from db import get_connection
from html_utils import escape_html, format_currency, html_page
from decimal import Decimal, InvalidOperation

bp = Blueprint("order", __name__)


@bp.post("/order")
def place_order():
    customer_id = request.form.get("customerId", "").strip()
    products = list(session.get("productList", {}).values())
    connection = None

    try:
        # 1. Validate customer ID, 400 = bad request 
        if not customer_id.isdecimal() or int(customer_id) <= 0:
            return html_page(
                "Invalid Customer",
                "<h1>Invalid Customer ID</h1>"
                "<p>Please enter a positive numeric customer ID.</p>"
            ), 400

        customer_id = int(customer_id)

        # 2. Check that the shopping cart is not empty
        if not products:
            return html_page(
                "Empty Shopping Cart",
                "<h1>Your shopping cart is empty.</h1>"
                '<a href="/listprod">Continue Shopping</a>'
            ), 400

        # 3. Connect to SQL Server
        connection = get_connection()
        cursor = connection.cursor()

        # 4. Check whether the customer exists, ? for row placeholder 
        cursor.execute("""
            SELECT customerId
            FROM customer
            WHERE customerId = ?
        """, customer_id)

        customer = cursor.fetchone() #retrives next avaible row 

        if customer is None:
            return html_page(
                "Customer Not Found",
                "<h1>Customer does not exist.</h1>"
                "<p>Please enter an existing customer ID.</p>"
            ), 400

        # 5. Validate cart items and calculate total, decimal is better to handle floating point erors 
        order_total = Decimal("0.00")
        validated_products = [] # list to store products 

        for product in products:
            product_id = int(product["id"])
            quantity = int(product["quantity"])
            price = Decimal(str(product["price"]))

            if product_id <= 0 or quantity <= 0: #we validate product id because of create url 
                raise ValueError("Invalid product or quantity")

            if not price.is_finite() or price < 0:
                raise ValueError("Invalid price") #jumps to exception block 

            order_total += price * quantity

            validated_products.append({
                "id": product_id,
                "name": str(product["name"]),
                "price": price,
                "quantity": quantity
            })

        # 6. Insert a new order and retrieve its ID
        cursor.execute("""
            INSERT INTO ordersummary
                (customerId, orderDate, totalAmount)
            OUTPUT INSERTED.orderId
            VALUES (?, GETDATE(), ?)
        """, customer_id, Decimal("0.00"))

        order_id = cursor.fetchone()[0]

        # 7. Insert every purchased product
        for product in validated_products:
            cursor.execute("""
                INSERT INTO orderproduct
                    (orderId, productId, quantity, price)
                VALUES (?, ?, ?, ?)
            """,
                order_id,
                product["id"],
                product["quantity"],
                product["price"]
            )

        # 8. Update the total order amount
        cursor.execute("""
            UPDATE ordersummary
            SET totalAmount = ?
            WHERE orderId = ?
        """, order_total, order_id)

        # 9. Save all database changes
        connection.commit()

        # 10. Clear the cart after successful commit
        session.pop("productList", None)

        # 11. Display order confirmation
        html = f"""
        <h1>Order Successfully Placed!</h1>
        <p>Order ID: {order_id}</p>
        <p>Customer ID: {customer_id}</p>

        <table border="1" cellpadding="5">
        <tr>
            <th>Product ID</th>
            <th>Product Name</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Subtotal</th>
        </tr>
        """

        for product in validated_products:
            subtotal = product["price"] * product["quantity"]

            html += f"""
            <tr>
                <td>{product["id"]}</td>
                <td>{escape_html(product["name"])}</td>
                <td>{product["quantity"]}</td>
                <td>{format_currency(product["price"])}</td>
                <td>{format_currency(subtotal)}</td>
            </tr>
            """

        html += f"""
        </table>
        <h2>Total: {format_currency(order_total)}</h2>
        <a href="/listprod">Continue Shopping</a>
        """

        return html_page("Grocery Order Confirmation", html)

    except (ValueError, InvalidOperation):
        if connection is not None:
            connection.rollback()

        return html_page(
            "Invalid Order",
            "<h1>Invalid shopping cart data.</h1>"
            "<p>Please review your cart and try again.</p>"
        ), 400

    except Exception:
        current_app.logger.exception("Unable to process order")

        # Undo any uncommitted database changes
        if connection is not None:
            connection.rollback()

        return html_page(
            "Order Processing Error",
            "<h1>Unable to process the order.</h1>"
        ), 500

    finally:
        # Close the database connection
        if connection is not None:
            connection.close()
