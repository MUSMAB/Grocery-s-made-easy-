
"""COSC 304 Lab 8: Product details and images."""

from flask import (
    Blueprint,
    request,
    current_app,
    url_for
)

from db import get_connection
from html_utils import (
    escape_html,
    format_currency,
    html_page
)

bp = Blueprint("product", __name__)


@bp.get("/product")
def product_details():

    # STEP 1: Get product ID from URL
    product_id = request.args.get("id", type=int)

    if product_id is None or product_id <= 0:

        return html_page(
            "Invalid Product",
            "<h1>Invalid product ID.</h1>"
        ), 400

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # STEP 2: Retrieve product using parameterized SQL
        cursor.execute("""
            SELECT
                productId,
                productName,
                productPrice,
                productDesc,
                productImageURL,
                productImage
            FROM product
            WHERE productId = ?
        """, product_id)

        product = cursor.fetchone()

        if product is None:

            return html_page(
                "Product Not Found",
                "<h1>Product not found.</h1>"
            ), 404

        # STEP 3: Build product information
        html = f"""
        <h1>{escape_html(product.productName)}</h1>

        <p>Product ID: {product.productId}</p>

        <h2>Price: {format_currency(product.productPrice)}</h2>
        """

        if product.productDesc:
            html += f"""
            <h3>Description</h3>
            <p>{escape_html(product.productDesc)}</p>
            """

        # STEP 4: Image from productImageURL
        image_url = product.productImageURL

        if image_url:

            image_url = str(image_url).strip()
            image_src = None

            # Full HTTP/HTTPS image address
            if image_url.startswith(("http://", "https://")):
                image_src = image_url

            # Relative path from SQL Server, e.g. img/1.jpg
            elif image_url.startswith("img/"):
                image_src = url_for(
                    "static",
                    filename=image_url
                )

            if image_src:

                html += f"""
                <h3>Product Image (URL)</h3>

                <img
                    src="{escape_html(image_src)}"
                    alt="{escape_html(product.productName)}"
                    style="max-width:300px; height:auto;"
                >
                """

        # STEP 5: Image from binary database field
        if product.productImage:

            binary_image_url = url_for(
                "display_image.display_image",
                id=product.productId
            )

            html += f"""
            <h3>Product Image (Database)</h3>

            <img
                src="{escape_html(binary_image_url)}"
                alt="{escape_html(product.productName)}"
                style="max-width:300px; height:auto;"
            >
            """

        # STEP 6: Add to Cart link
        cart_url = url_for(
            "addcart.add_to_cart",
            id=product.productId,
            name=product.productName,
            price=product.productPrice
        )

        # STEP 7: Continue Shopping link
        shop_url = url_for(
            "listprod.list_products"
        )

        html += f"""
        <p>
            <a
                class="button"
                href="{escape_html(cart_url)}"
            >
                Add to Cart
            </a>

            <a
                class="button secondary"
                href="{escape_html(shop_url)}"
            >
                Continue Shopping
            </a>
        </p>
        """

        return html_page(
            "Product Details",
            html
        )

    except Exception:

        current_app.logger.exception(
            "Unable to display product details"
        )

        return html_page(
            "Product Error",
            "<h1>Unable to display product.</h1>"
        ), 500

    finally:
        if connection is not None:
            connection.close()
