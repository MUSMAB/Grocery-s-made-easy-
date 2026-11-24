
"""Shared HTML helpers and store page layout."""

from decimal import Decimal
from html import escape


def escape_html(value):
    return escape(
        "" if value is None else str(value),
        quote=True
    )


def format_currency(value):
    return f"${Decimal(str(value)):.2f}"


def html_page(title, body):
    return f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="utf-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <title>{escape_html(title)}</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                background: #f7f8fa;
                color: #222;
            }}

            header {{
                background: #234b36;
                color: white;
                padding: 20px 35px;
            }}

            header h1 {{
                margin: 0 0 15px 0;
                font-size: 25px;
            }}

            nav a {{
                display: inline-block;
                color: white;
                text-decoration: none;
                margin-right: 12px;
                padding: 8px 12px;
                border-radius: 5px;
            }}

            nav a:hover {{
                background: #376b4e;
            }}

            main {{
                max-width: 1100px;
                margin: 30px auto;
                padding: 25px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px #00000010;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}

            th {{
                background: #e7f0e9;
            }}

            tr:nth-child(even) {{
                background: #f9faf9;
            }}

            input {{
                padding: 7px;
                margin: 4px;
            }}

            button, .button {{
                display: inline-block;
                background: #276a47;
                color: white;
                border: none;
                padding: 9px 14px;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                margin: 3px;
            }}

            button:hover, .button:hover {{
                background: #17472e;
            }}

            .button.secondary {{
                background: #667085;
            }}

            @media (max-width: 600px) {{
                main {{
                    margin: 10px;
                    padding: 12px;
                    overflow-x: auto;
                }}
            }}
        </style>
    </head>

    <body>
        <header>
            <h1>Mustafa and lamia's Grocery</h1>

            
            <nav>
            <a href="/">Home</a>
            <a href="/listprod">Search Products</a>
            <a href="/listorder">All Orders</a>
            <a href="/showcart">Shopping Cart</a>

            <a href="/login">Login</a>
            <a href="/customer">My Account</a>
            <a href="/admin">Admin Report</a>

            <a href="/shipment-tests">Shipment Tests</a>
            <a href="/logout">Logout</a>
            </nav>

        </header>

        <main>
            {body}
        </main>
    </body>

    </html>
    """

