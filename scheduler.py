# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Scheduler File
# =============================================

import schedule
import time
from database import get_all_products, save_price_history, update_current_price
from scraper import check_price
from alerts import check_target_price_alert, check_price_drop_alert
from config import CHECK_INTERVAL_HOURS


def track_all_products():
    print("Starting price tracking for all products...")
    products = get_all_products()

    if not products:
        print("No products to track!")
        return

    for product in products:
        product_id = product[0]
        product_name = product[1]
        product_url = product[2]
        product_site = product[3]
        target_price = product[4]
        email = product[5]
        old_price = product[6]

        try:
            print(f"Tracking: {product_name}")
            current_price = check_price(product)

            if current_price is None:
                print(f"Could not get price for {product_name} — skipping")
                continue

            save_price_history(product_id, current_price)
            update_current_price(product_id, current_price)

            check_target_price_alert(
                product_name, current_price, target_price,
                product_site, product_url, email
            )
            check_price_drop_alert(
                product_name, old_price, current_price,
                product_site, product_url, email
            )

            print(f"Done: {product_name} — ₹{current_price}")

        except Exception as e:
            print(f"Error tracking {product_name}: {e}")
            continue

    print("All products tracked.")


def start_scheduler():
    print(f"Scheduler started — every {CHECK_INTERVAL_HOURS} hours")
    track_all_products()
    schedule.every(CHECK_INTERVAL_HOURS).hours.do(track_all_products)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler()