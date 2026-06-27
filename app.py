# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Main Flask Application File
# =============================================

from flask import Flask, render_template, request, redirect, url_for
from database import (
    create_tables, save_product, save_price_history,
    get_all_products, get_product_by_id, delete_product
)
from scraper import scrape_direct_url, detect_site
from ml_model import predict_price, generate_chart
import threading
import scheduler

app = Flask(__name__)
create_tables()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/track-url", methods=["POST"])
def track_url():
    product_url = request.form.get("product_url", "").strip()
    target_price = request.form.get("target_price")
    email = request.form.get("email")

    if not product_url or not target_price or not email:
        return render_template("index.html", error="Please fill all fields!")

    site = detect_site(product_url)
    if not site:
        return render_template("index.html", error="Only Amazon, Flipkart and Nykaa URLs are supported!")

    result = scrape_direct_url(product_url)

    if not result:
        return render_template(
            "index.html",
            error=f"Could not read product details from that {site} URL. "
                  f"The page may be blocking access — please try a different product link."
        )

    product_id = save_product(
        result["name"], product_url, site,
        float(target_price), email, result["price"]
    )
    save_price_history(product_id, result["price"])

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    products = get_all_products()
    product_data = []

    for product in products:
        product_id = product[0]
        current_price = product[6]
        target_price = product[4]

        prediction, _ = predict_price(product_id)
        status = _compute_status(current_price, target_price, prediction)

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
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for("dashboard"))

    prediction, _ = predict_price(product_id)
    chart_path = generate_chart(product_id, product[1])
    status = _compute_status(product[6], product[4], prediction)

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
def delete_product_route(product_id):
    delete_product(product_id)
    return redirect(url_for("dashboard"))


def _compute_status(current_price, target_price, prediction):
    if current_price and target_price:
        if current_price <= target_price:
            return "✅ Below Target"
        elif prediction and prediction["slope"] > 0:
            return "📈 Price Rising"
        elif prediction and prediction["slope"] < 0:
            return "📉 Price Dropping"
    return "⏳ Collecting data..."


def run_scheduler():
    scheduler.start_scheduler()


if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    app.run(debug=True)