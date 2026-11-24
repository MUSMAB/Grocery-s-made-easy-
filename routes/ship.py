
"""COSC 304 Lab 8: Shipment processing with SQL transactions."""

from flask import (
    Blueprint,
    request,
    current_app
)

from db import get_connection
from html_utils import escape_html, html_page

bp = Blueprint("ship", __name__)

WAREHOUSE_ID = 1


class ShipmentError(Exception):
    """An error that prevents the entire shipment."""


@bp.get("/ship")
def ship_order():

    # STEP 1: Validate the order ID
    raw_order_id = request.args.get("orderId", "")

    try:
        order_id = int(raw_order_id)

        if order_id <= 0 or order_id > 2147483647:
            raise ValueError()

    except (ValueError, TypeError):

        return html_page(
            "Shipment Error",
            "<h1>Invalid order ID.</h1>"
        ), 400

    connection = None

    try:
        # STEP 2: Open a database connection
        connection = get_connection()

        # All SQL changes belong to one transaction
        connection.autocommit = False

        cursor = connection.cursor()

        # STEP 3: Check whether the order exists
        cursor.execute("""
            SELECT orderId
            FROM ordersummary
            WHERE orderId = ?
        """, order_id)

        if cursor.fetchone() is None:
            raise ShipmentError("Order not found.")

        # STEP 4: Retrieve all products in the order
        cursor.execute("""
            SELECT
                productId,
                SUM(quantity) AS orderedQuantity
            FROM orderproduct
            WHERE orderId = ?
            GROUP BY productId
            ORDER BY productId
        """, order_id)

        products = cursor.fetchall()

        if not products:
            raise ShipmentError(
                "The selected order contains no products."
            )

        # STEP 5: Verify warehouse 1 exists
        cursor.execute("""
            SELECT warehouseId
            FROM warehouse
            WHERE warehouseId = ?
        """, WAREHOUSE_ID)

        if cursor.fetchone() is None:
            raise ShipmentError(
                "Warehouse 1 does not exist."
            )

        # STEP 6: Create a shipment record
        # This is part of the same transaction.
        cursor.execute("""
            INSERT INTO shipment (
                shipmentDate,
                shipmentDesc,
                warehouseId
            )
            VALUES (
                GETDATE(),
                ?,
                ?
            )
        """,
            f"Shipment for order {order_id}",
            WAREHOUSE_ID
        )

        shipment_results = []

        # STEP 7: Process every product
        for product in products:

            product_id = int(product.productId)
            ordered_qty = int(product.orderedQuantity)

            if ordered_qty <= 0:
                raise ShipmentError(
                    f"Invalid quantity for product id: {product_id}"
                )

            # Read inventory and lock the row
            # while the transaction is processing.
            cursor.execute("""
                SELECT quantity
                FROM productinventory WITH (UPDLOCK, HOLDLOCK)
                WHERE productId = ?
                  AND warehouseId = ?
            """, product_id, WAREHOUSE_ID)

            inventory = cursor.fetchone()

            if inventory is None:
                raise ShipmentError(
                    f"Insufficient inventory for product id: {product_id}"
                )

            previous_qty = int(inventory.quantity)

            # STEP 8: Check sufficient inventory
            if previous_qty < ordered_qty:
                raise ShipmentError(
                    f"Insufficient inventory for product id: {product_id}"
                )

            # STEP 9: Update the inventory
            cursor.execute("""
                UPDATE productinventory
                SET quantity = quantity - ?
                WHERE productId = ?
                  AND warehouseId = ?
                  AND quantity >= ?
            """,
                ordered_qty,
                product_id,
                WAREHOUSE_ID,
                ordered_qty
            )

            if cursor.rowcount != 1:
                raise ShipmentError(
                    f"Unable to update inventory for product id: {product_id}"
                )

            new_qty = previous_qty - ordered_qty

            shipment_results.append({
                "product_id": product_id,
                "ordered_qty": ordered_qty,
                "previous_qty": previous_qty,
                "new_qty": new_qty
            })

        # STEP 10: Commit only if EVERY product succeeded
        connection.commit()

        # Display successful shipment
        html = f"""
        <h1>Shipment Successfully Processed!</h1>

        <p>Order ID: {order_id}</p>
        <p>Warehouse ID: {WAREHOUSE_ID}</p>

        <table>
            <thead>
                <tr>
                    <th>Product ID</th>
                    <th>Ordered Quantity</th>
                    <th>Previous Inventory</th>
                    <th>New Inventory</th>
                </tr>
            </thead>
            <tbody>
        """

        for item in shipment_results:

            html += f"""
            <tr>
                <td>{item["product_id"]}</td>
                <td>{item["ordered_qty"]}</td>
                <td>{item["previous_qty"]}</td>
                <td>{item["new_qty"]}</td>
            </tr>
            """

        html += """
            </tbody>
        </table>

        <p>
            <strong>Shipment successfully processed.</strong>
        </p>

        <p><a href="/">Back to Main Page</a></p>
        """

        return html_page(
            "Shipment Successful",
            html
        )

    except ShipmentError as error:

        # STEP 11: Roll back ALL changes
        if connection is not None:
            connection.rollback()

        html = f"""
        <h1>Shipment Not Completed</h1>

        <p>
            Shipment not done.
            {escape_html(str(error))}
        </p>

        <p>
            All inventory changes and the shipment
            record were rolled back.
        </p>

        <p><a href="/">Back to Main Page</a></p>
        """

        return html_page(
            "Shipment Failed",
            html
        ), 400

    except Exception:

        # Unexpected database error
        if connection is not None:
            connection.rollback()

        current_app.logger.exception(
            "Unable to process shipment for order %s",
            order_id
        )

        return html_page(
            "Shipment Error",
            """
            <h1>Shipment Error</h1>

            <p>
                Shipment not completed.
                Database changes were rolled back.
            </p>

            <p><a href="/">Back to Main Page</a></p>
            """
        ), 500

    finally:
        if connection is not None:
            connection.close()

