
"""Display, update, and remove products from the shopping cart."""

from decimal import Decimal
from flask import Blueprint, session, request, redirect, url_for
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("showcart", __name__)


@bp.get("/showcart")
def show_cart():
    products = list(session.get("productList", {}).values())

    if not products:
        return html_page(
            "Your Shopping Cart",
            '<h1>Your shopping cart is empty!</h1>'
            '<p><a href="/listprod">Continue Shopping</a></p>'
        )

    total = Decimal("0.00")
    rows = []

    for product in products:
        product_id = str(product["id"])
        quantity = int(product["quantity"])
        price = Decimal(str(product["price"]))
        subtotal = price * quantity
        total += subtotal

        rows.append(f"""
        <tr>
            <td>{escape_html(product_id)}</td>
            <td>{escape_html(product["name"])}</td>
            <td>{format_currency(price)}</td>
            <td>
                <form method="post" action="/updatecart">
                    <input type="hidden"
                           name="productId"
                           value="{escape_html(product_id)}">

                    <input type="number"
                           name="quantity"
                           value="{quantity}"
                           min="1"
                           max="9999"
                           required
                           style="width:65px;">

                    <button type="submit"
                            name="action"
                            value="update">
                        Update
                    </button>

                    <button type="submit"
                            name="action"
                            value="remove"
                            formnovalidate>
                        Remove
                    </button>
                </form>
            </td>
            <td>{format_currency(subtotal)}</td>
        </tr>
        """)

    html = f"""
    <h1>Your Shopping Cart</h1>

    <table>
        <thead>
            <tr>
                <th>Product ID</th>
                <th>Product Name</th>
                <th>Unit Price</th>
                <th>Quantity / Actions</th>
                <th>Subtotal</th>
            </tr>
        </thead>

        <tbody>
            {"".join(rows)}
        </tbody>

        <tfoot>
            <tr>
                <td colspan="4"><strong>Order Total</strong></td>
                <td><strong>{format_currency(total)}</strong></td>
            </tr>
        </tfoot>
    </table>

    <p>
        <a class="button" href="/checkout">Proceed to Checkout</a>
        <a class="button secondary" href="/listprod">
            Continue Shopping
        </a>
    </p>
    """

    return html_page("Your Shopping Cart", html)


@bp.post("/updatecart")
def update_cart():
    product_id = request.form.get("productId", "")
    action = request.form.get("action", "")

    # Copy the cart so Flask saves the session changes
    cart = dict(session.get("productList", {}))

    if product_id not in cart:
        return html_page(
            "Invalid Product",
            "<h1>Product not found in cart.</h1>"
        ), 400

    if action == "remove":
        # Delete the selected product
        cart.pop(product_id)

    elif action == "update":
        quantity_text = request.form.get("quantity", "")

        # Validate the new quantity
        if not quantity_text.isdecimal():
            return html_page(
                "Invalid Quantity",
                "<h1>Please enter a valid quantity.</h1>"
            ), 400

        quantity = int(quantity_text)

        if quantity < 1 or quantity > 9999:
            return html_page(
                "Invalid Quantity",
                "<h1>Quantity must be between 1 and 9999.</h1>"
            ), 400

        # Update the selected product
        product = dict(cart[product_id])
        product["quantity"] = quantity
        cart[product_id] = product

    else:
        return html_page(
            "Invalid Action",
            "<h1>Unsupported cart action.</h1>"
        ), 400

    # Store the updated cart in Flask's session
    session["productList"] = cart

    # Return to the shopping cart page
    return redirect(url_for("showcart.show_cart"))
