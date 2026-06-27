# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Main Flask Application File
# =============================================

from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, save_product, save_price_history, get_all_products, update_current_price
from scraper import compare_prices, scrape_direct_url
from ml_model import predict_price, generate_chart
import threading
import scheduler
import sqlite3
from config import DATABASE_NAME

app = Flask(__name__)

create_tables()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    product_name = request.form.get("product_name")
    target_price = request.form.get("target_price")
    email = request.form.get("email")

    if not product_name or not target_price or not email:
        return render_template("index.html", error="Please fill all fields!")

    results = compare_prices(product_name)

    if not results:
        return render_template("index.html", error="No results found! Try different product name.")

    return render_template("results.html",
                           results=results,
                           product_name=product_name,
                           target_price=target_price,
                           email=email)

@app.route("/track-url", methods=["POST"])
def track_url():
    product_url = request.form.get("product_url")
    target_price = request.form.get("target_price")
    email = request.form.get("email")

    if not product_url or not target_price or not email:
        return render_template("index.html", error="Please fill all fields!")

    if "amazon" in product_url:
        site = "Amazon"
    elif "flipkart" in product_url:
        site = "Flipkart"
    elif "nykaa" in product_url:
        site = "Nykaa"
    else:
        return render_template("index.html", error="Only Amazon, Flipkart and Nykaa URLs are supported!")

    result = scrape_direct_url(product_url)

    if not result:
        return render_template("index.html", error="Could not get product details! Please check the URL.")

    product_id = save_product(
        result["name"],
        product_url,
        site,
        float(target_price),
        email,
        result["price"]
    )

    save_price_history(product_id, result["price"])

    return redirect(url_for("dashboard"))

@app.route("/track", methods=["POST"])
def track():
    product_name = request.form.get("product_name")
    product_url = request.form.get("url")
    product_site = request.form.get("site")
    current_price = float(request.form.get("price"))
    target_price = float(request.form.get("target_price"))
    email = request.form.get("email")

    product_id = save_product(
        product_name,
        product_url,
        product_site,
        target_price,
        email,
        current_price
    )

    save_price_history(product_id, current_price)

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    products = get_all_products()
    product_data = []

    for product in products:
        product_id = product[0]
        current_price = product[6]
        target_price = product[4]

        prediction, error = predict_price(product_id)

        if current_price and target_price:
            if current_price <= target_price:
                status = "✅ Below Target"
            elif prediction and prediction["slope"] > 0:
                status = "📈 Price Rising"
            elif prediction and prediction["slope"] < 0:
                status = "📉 Price Dropping"
            else:
                status = "⏳ Waiting"
        else:
            status = "⏳ Waiting"

        product_data.append({
            "id": product_id,
            "name": product[1],
            "site": product[3],
            "current_price": current_price,
            "target_price": target_price,
            "email": product[5],
            "status": status,
            "prediction": prediction,
        })

    return render_template("dashboard.html", products=product_data)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        return redirect(url_for("dashboard"))

    prediction, error = predict_price(product_id)
    chart_path = generate_chart(product_id, product[1])

    if product[6] and product[4]:
        if product[6] <= product[4]:
            status = "✅ Below Target"
        elif prediction and prediction["slope"] > 0:
            status = "📈 Price Rising"
        elif prediction and prediction["slope"] < 0:
            status = "📉 Price Dropping"
        else:
            status = "⏳ Waiting"
    else:
        status = "⏳ Waiting"

    product_data = {
        "id": product[0],
        "name": product[1],
        "url": product[2],
        "site": product[3],
        "target_price": product[4],
        "email": product[5],
        "current_price": product[6],
        "status": status,
        "prediction": prediction,
        "chart_path": chart_path
    }

    return render_template("product.html", product=product_data)

@app.route("/delete/<int:product_id>")
def delete_product(product_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    cursor.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/update-now/<int:product_id>")
def update_now(product_id):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()

        if product:
            product_name = product[1]
            target_price = product[4]
            email = product[5]
            old_price = product[6]

            results = compare_prices(product_name)
            if results:
                current_price = results[0]["price"]
                current_site = results[0]["site"]
                current_url = results[0]["url"]

                save_price_history(product_id, current_price)
                update_current_price(product_id, current_price)

                from alerts import check_target_price_alert, check_price_drop_alert
                check_target_price_alert(product_name, current_price, target_price, current_site, current_url, email)
                check_price_drop_alert(product_name, old_price, current_price, current_site, current_url, email)

    except Exception as e:
        print(f"Update error: {e}")

    return redirect(url_for("dashboard"))

def run_scheduler():
    scheduler.start_scheduler()

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    app.run(debug=True)