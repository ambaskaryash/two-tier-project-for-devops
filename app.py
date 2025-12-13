import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# ----------------------------
# MySQL Configuration
# ----------------------------
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

mysql = MySQL(app)

# ----------------------------
# Sample Product Catalog
# ----------------------------
PRODUCTS = [
    {"id": 1, "name": "DevOps Hoodie", "price": 1999, "image": "https://via.placeholder.com/300"},
    {"id": 2, "name": "Linux T-Shirt", "price": 999, "image": "https://via.placeholder.com/300"},
    {"id": 3, "name": "Cloud Sticker Pack", "price": 299, "image": "https://via.placeholder.com/300"},
]

# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)


@app.route("/order", methods=["POST"])
def place_order():
    data = request.get_json() or request.form
    name = data.get("name")
    product = data.get("product")

    if not name or not product:
        return jsonify({"error": "Missing details"}), 400

    message = f"Order placed by {name} for product: {product}"

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (message) VALUES (%s)", (message,))
    mysql.connection.commit()
    cur.close()

    return jsonify({"status": "success", "message": "Order placed successfully"})

@app.route("/orders")
def order_history():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, message FROM messages ORDER BY id DESC")
    orders = cur.fetchall()
    cur.close()
    return render_template("orders.html", orders=orders)


@app.route("/admin")
def admin_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM messages")
    total_orders = cur.fetchone()[0]

    cur.execute("SELECT id, message FROM messages ORDER BY id DESC LIMIT 10")
    recent_orders = cur.fetchall()
    cur.close()

    return render_template(
        "admin.html",
        total_orders=total_orders,
        recent_orders=recent_orders
    )



# ----------------------------
# App Runner
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
