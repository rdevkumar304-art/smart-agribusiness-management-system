from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB_PATH = Path(__file__).with_name("agribusiness.db")


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                sold_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)


@app.route("/")
def index():
    with get_db() as db:
        products = db.execute("SELECT * FROM products ORDER BY name").fetchall()
        sales = db.execute("""
            SELECT sales.*, products.name AS product_name
            FROM sales JOIN products ON sales.product_id = products.id
            ORDER BY sales.id DESC LIMIT 10
        """).fetchall()
        total_products = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        stock_units = db.execute("SELECT COALESCE(SUM(quantity), 0) FROM products").fetchone()[0]
        total_sales = db.execute("SELECT COALESCE(SUM(total), 0) FROM sales").fetchone()[0]
    return render_template(
        "index.html", products=products, sales=sales,
        total_products=total_products, stock_units=stock_units, total_sales=total_sales
    )


@app.route("/add-product", methods=["POST"])
def add_product():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    try:
        quantity = int(request.form.get("quantity", "0"))
        price = float(request.form.get("price", "0"))
    except ValueError:
        flash("Quantity and price must be valid numbers.", "error")
        return redirect(url_for("index"))

    if not name or not category or quantity < 0 or price < 0:
        flash("Enter a product name, category, and non-negative quantity and price.", "error")
        return redirect(url_for("index"))

    with get_db() as db:
        db.execute(
            "INSERT INTO products (name, category, quantity, price) VALUES (?, ?, ?, ?)",
            (name, category, quantity, price)
        )
    flash("Product added successfully.", "success")
    return redirect(url_for("index"))


@app.route("/record-sale", methods=["POST"])
def record_sale():
    try:
        product_id = int(request.form.get("product_id", "0"))
        quantity_sold = int(request.form.get("quantity_sold", "0"))
    except ValueError:
        flash("Choose a product and enter a valid quantity.", "error")
        return redirect(url_for("index"))

    if quantity_sold <= 0:
        flash("Sale quantity must be greater than zero.", "error")
        return redirect(url_for("index"))

    with get_db() as db:
        product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            flash("Product not found.", "error")
            return redirect(url_for("index"))
        if quantity_sold > product["quantity"]:
            flash(f"Not enough stock. Available quantity: {product['quantity']}.", "error")
            return redirect(url_for("index"))

        total = quantity_sold * product["price"]
        db.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?",
                   (quantity_sold, product_id))
        db.execute("INSERT INTO sales (product_id, quantity, total) VALUES (?, ?, ?)",
                   (product_id, quantity_sold, total))

    flash("Sale recorded and stock updated.", "success")
    return redirect(url_for("index"))


@app.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    with get_db() as db:
        has_sales = db.execute("SELECT COUNT(*) FROM sales WHERE product_id = ?",
                               (product_id,)).fetchone()[0]
        if has_sales:
            flash("This product has sales records, so it cannot be deleted.", "error")
        else:
            db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            flash("Product deleted.", "success")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
