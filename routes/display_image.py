
"""COSC 304 Lab 8: Display binary product images."""

from flask import (
    Blueprint,
    Response,
    current_app,
    request
)

from db import get_connection

bp = Blueprint("display_image", __name__)


@bp.get("/displayImage")
def display_image():

    # STEP 1: Read product ID
    raw_id = request.args.get("id", "")

    try:
        product_id = int(raw_id)

        if product_id <= 0 or product_id > 2147483647:
            raise ValueError()

    except (ValueError, TypeError):
        return "Invalid product ID", 400

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # STEP 2: Retrieve the binary image
        # using a parameterized SQL query.
        cursor.execute("""
            SELECT productImage
            FROM product
            WHERE productId = ?
        """, product_id)

        row = cursor.fetchone()

        if row is None:
            return "Product not found", 404

        if row[0] is None:
            return "No database image for this product", 404

        # STEP 3: Convert SQL binary data to bytes
        image_data = bytes(row[0])

        if not image_data:
            return "No database image for this product", 404

        # STEP 4: Return image bytes to the browser
        return Response(
            image_data,
            mimetype="image/jpeg"
        )

    except Exception:

        current_app.logger.exception(
            "Unable to retrieve database image"
        )

        return "Unable to retrieve product image", 500

    finally:
        if connection is not None:
            connection.close()
