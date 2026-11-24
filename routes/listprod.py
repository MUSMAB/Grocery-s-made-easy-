
"""COSC 304: Display/search products and provide cart links."""

from flask import Blueprint, request, current_app, url_for

from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("listprod", __name__)


@bp.get("/listprod")
def list_products():

    # Get product search term from the URL
    name = request.args.get("productName", "")

    # Search form
    form = (
        "<h1>Search for the products you want to buy:</h1>"
        '<form method="get" action="/listprod">'
        f'<input type="text" name="productName" '
        f'size="50" value="{escape_html(name)}">'
        '<input type="submit" value="Submit"> '
        '<input type="reset" value="Reset"> '
        '(Leave blank for all products)'
        '</form>'
    )

    connection = None

    try:
        # STEP 1: Connect to SQL Server
        connection = get_connection()
        cursor = connection.cursor()

        # STEP 2: Search using a parameterized SQL query
        if name.strip():

            cursor.execute("""
                SELECT
                    productId,
                    productName,
                    productPrice
                FROM product
                WHERE productName LIKE ?
                ORDER BY productName
            """, f"%{name.strip()}%")

        else:

            cursor.execute("""
                SELECT
                    productId,
                    productName,
                    productPrice
                FROM product
                ORDER BY productName
            """)

        products = cursor.fetchall()

        # STEP 3: Build product table
        html = """
        <table>
            <thead>
                <tr>
                    <th>Product ID</th>
                    <th>Product Name</th>
                    <th>Price</th>
                    <th>Add to Cart</th>
                </tr>
            </thead>
            <tbody>
        """

        # STEP 4: Display every returned product
        for product in products:

            # Add to Cart link
            cart_url = url_for(
                "addcart.add_to_cart",
                id=product.productId,
                name=product.productName,
                price=product.productPrice
            )

            # Lab 8: Product detail link
            # Correct function name is product_details
            detail_url = url_for(
                "product.product_details",
                id=product.productId
            )

            html += f"""
            <tr>
                <td>{product.productId}</td>

                <td>
                    <a href="{escape_html(detail_url)}">
                        {escape_html(product.productName)}
                    </a>
                </td>

                <td>
                    {format_currency(product.productPrice)}
                </td>

                <td>
                    <a href="{escape_html(cart_url)}">
                        Add to Cart
                    </a>
                </td>
            </tr>
            """

        html += """
            </tbody>
        </table>
        """

        # Display message if no matching products
        if not products:
            html += "<p>No matching products found.</p>"

        return html_page(
            "Product Search",
            form + html
        )

    except Exception:

        current_app.logger.exception(
            "Unable to list products"
        )

        return html_page(
            "Product Search Error",
            form + "<p>Unable to search products.</p>"
        ), 500

    finally:
        if connection is not None:
            connection.close()

