
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "change-this-secret-before-production"

PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones", "price": 1499},
    {"id": 2, "name": "Smart Watch", "price": 2499},
    {"id": 3, "name": "Laptop Bag", "price": 799},
    {"id": 4, "name": "Bluetooth Speaker", "price": 1199},
]

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Online Shopping</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {font-family:Arial;background:#f1f5f9;margin:0;color:#1e293b}
header {background:#4338ca;color:white;padding:22px;text-align:center}
main {max-width:900px;margin:25px auto;padding:15px}
.pipeline,.card {background:white;padding:20px;margin-bottom:18px;
border-radius:12px;box-shadow:0 3px 12px #00000010}
.pipeline {text-align:center;line-height:2;background:#e0e7ff}
.products {display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:15px}
button {background:#4338ca;color:white;border:0;padding:10px 15px;
border-radius:7px;cursor:pointer}
input {padding:10px;width:65px}
.price {color:#15803d;font-weight:bold}
.notice {background:#dcfce7;padding:12px;border-radius:7px}
</style>
</head>
<body>
<header><h1>Online Shopping Store</h1>
<p>Shop easily and manage your cart</p></header>
<main>
<div class="pipeline"><b>SHOPPING PIPELINE</b><br>
Browse Products → Add to Cart → Validate Cart → Checkout → Confirmation
</div>

{% if message %}
<div class="notice">{{ message }}</div><br>
{% endif %}

<h2>Available Products</h2>
<div class="products">
{% for product in products %}
<div class="card">
<h3>{{ product["name"] }}</h3>
<p class="price">₹{{ product["price"] }}</p>
<form method="post" action="/add/{{ product['id'] }}">
<label>Quantity </label>
<input type="number" name="quantity" value="1" min="1" max="20" required>
<button type="submit">Add to Cart</button>
</form>
</div>
{% endfor %}
</div>

<div class="card">
<h2>Your Shopping Cart</h2>
{% if cart_items %}
{% for item in cart_items %}
<p>{{ item["name"] }} × {{ item["quantity"] }}
— ₹{{ item["subtotal"] }}</p>
{% endfor %}
<hr>
<h3>Total: ₹{{ total }}</h3>
<form method="post" action="/checkout">
<button type="submit">Checkout</button>
</form>
<form method="post" action="/clear">
<button type="submit" style="background:#dc2626;margin-top:10px">
Clear Cart</button>
</form>
{% else %}
<p>Your cart is empty. Add a product to begin.</p>
{% endif %}
</div>
</main>
</body>
</html>
"""


def build_cart(cart):
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = next(
            (p for p in PRODUCTS if p["id"] == int(product_id)),
            None
        )

        if product is None:
            continue

        subtotal = product["price"] * quantity
        items.append({
            "name": product["name"],
            "quantity": quantity,
            "subtotal": subtotal
        })
        total += subtotal

    return items, total


@app.route("/")
def home():
    cart = session.get("cart", {})
    items, total = build_cart(cart)

    return render_template_string(
        HTML,
        products=PRODUCTS,
        cart_items=items,
        total=total,
        message=request.args.get("message", "")
    )


@app.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = next(
        (p for p in PRODUCTS if p["id"] == product_id),
        None
    )

    if product is None:
        return redirect(url_for("home", message="Product not found."))

    try:
        quantity = int(request.form.get("quantity", "1"))
    except (ValueError, TypeError):
        return redirect(url_for("home", message="Invalid quantity."))

    if not 1 <= quantity <= 20:
        return redirect(url_for("home", message="Quantity must be 1 to 20."))

    cart = session.get("cart", {})
    key = str(product_id)
    new_quantity = cart.get(key, 0) + quantity

    if new_quantity > 20:
        return redirect(url_for("home", message="Maximum quantity is 20."))

    cart[key] = new_quantity
    session["cart"] = cart

    return redirect(url_for("home", message="Product added to cart!"))


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", {})

    if not cart:
        return redirect(url_for("home", message="Your cart is empty."))

    items, total = build_cart(cart)

    if not items or total <= 0:
        return redirect(url_for("home", message="Unable to process cart."))

    session["cart"] = {}

    return redirect(url_for(
        "home",
        message=f"Order placed successfully! Demo total: Rs. {total}"
    ))


@app.route("/clear", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("home", message="Cart cleared."))


@app.errorhandler(404)
def not_found(error):
    return "Page not found.", 404


@app.errorhandler(500)
def server_error(error):
    return "Unexpected server error. Please try again.", 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
