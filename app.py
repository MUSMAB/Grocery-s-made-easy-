
"""COSC 304 Lab 7 and Lab 8 Grocery Store."""

import os
from pathlib import Path

from flask import Flask, send_file

from html_utils import html_page

# ---------------------------------------------
# LAB 7 ROUTES
# ---------------------------------------------

from routes import (
    addcart,
    checkout,
    listorder,
    listprod,
    loaddata,
    order,
    showcart
)

# ---------------------------------------------
# LAB 8 ROUTES
# ---------------------------------------------

from routes.product import bp as product_bp
from routes.display_image import bp as display_image_bp
from routes.login import bp as login_bp
from routes.validate_login import bp as validate_login_bp
from routes.logout import bp as logout_bp
from routes.admin import bp as admin_bp
from routes.customer import bp as customer_bp
from routes.ship import bp as ship_bp

from examples import register_examples


# ---------------------------------------------
# CREATE FLASK APPLICATION
# ---------------------------------------------

app = Flask(__name__)

# Flask session secret key
# Use an environment variable in production.
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "cosc304-local-lab-session-secret"
)


# ---------------------------------------------
# HOME PAGE
# ---------------------------------------------

@app.get("/")
def index():
    return send_file(
        Path(__file__).parent / "views" / "index.html"
    )


# ---------------------------------------------
# LAB 8: SHIPMENT TEST MENU
# ---------------------------------------------

@app.get("/shipment-tests")
def shipment_tests():

    html = """
    <h1>Shipment Testing</h1>

    <p>
        Test the Lab 8 shipment functionality
        using Warehouse 1.
    </p>

    <h2>Test 1: Successful Shipment</h2>

    <p>
        Process Order ID 1.
        This shipment should succeed if Warehouse 1
        has sufficient inventory.
    </p>

    <p>
        <strong>Important:</strong>
        Successful shipments reduce inventory.
        Do not repeatedly process the same order.
    </p>

    <p>
        <a class="button" href="/ship?orderId=1">
            Process Order 1
        </a>
    </p>

    <h2>Test 2: Insufficient Inventory</h2>

    <p>
        Process Order ID 3.
        With the original lab data, this shipment
        should fail due to insufficient inventory.
    </p>

    <p>
        All inventory updates and the shipment record
        must be rolled back when a product cannot
        be shipped.
    </p>

    <p>
        <a class="button secondary" href="/ship?orderId=3">
            Process Order 3
        </a>
    </p>

    <p>
        <a href="/">Back to Main Page</a>
    </p>
    """

    return html_page(
        "Shipment Tests",
        html
    )


# ---------------------------------------------
# REGISTER LAB 7 ROUTES
# ---------------------------------------------

for module in (
    loaddata,
    listorder,
    listprod,
    addcart,
    showcart,
    checkout,
    order
):
    app.register_blueprint(module.bp)


# ---------------------------------------------
# REGISTER LAB 8 ROUTES
# ---------------------------------------------

# Product details and images (10 marks)
app.register_blueprint(product_bp)
app.register_blueprint(display_image_bp)

# Login and administrator sales report (5 marks)
app.register_blueprint(login_bp)
app.register_blueprint(validate_login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(admin_bp)

# Customer information (5 marks)
app.register_blueprint(customer_bp)

# Shipment transactions (5 marks)
app.register_blueprint(ship_bp)


# ---------------------------------------------
# EXISTING EXAMPLE ROUTES
# ---------------------------------------------

register_examples(app)


# ---------------------------------------------
# START FLASK APPLICATION
# ---------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=True
    )
