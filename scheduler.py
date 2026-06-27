# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Scheduler File
# =============================================

import schedule
import time
from database import get_all_products, save_price_history, update_current_price
from scraper import compare_prices
from alerts import check_target_price_alert, check_price_drop_alert
from config import CHECK_INTERVAL_HOURS

def track_all_products():
    print("Starting price tracking for all products...")

    products = get_all_products()

    if not products:
        print("No products to track!")
        return

    for product in products:
        try:
            product_id = product[0]
            product_name = product[1]
            target_price = product[4]
            email = product[5]
            old_price = product[6]

            print(f"Tracking: {product_name}")

            results = compare_prices(product_name)

            if not results:
                print(f"Could not find price for {product_name}")
                time.sleep(5)
                continue

            best_result = results[0]
            current_price = best_result["price"]
            current_site = best_result["site"]
            current_url = best_result["url"]

            save_price_history(product_id, current_price)
            update_current_price(product_id, current_price)

            check_target_price_alert(
                product_name, current_price, target_price,
                current_site, current_url, email
            )

            check_price_drop_alert(
                product_name, old_price, current_price,
                current_site, current_url, email
            )

            print(f"Done: {product_name} — ₹{current_price}")
            time.sleep(5)

        except Exception as e:
            print(f"Error tracking {product_name}: {e}")
            continue

    print("All products tracked!")

def start_scheduler():
    print(f"Scheduler started — tracking every {CHECK_INTERVAL_HOURS} hours")
    track_all_products()
    schedule.every(CHECK_INTERVAL_HOURS).hours.do(track_all_products)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler()