# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Configuration File
# =============================================

import os

# --- ScraperAPI Key ---
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY", "f4952c74f509965964a0a6d45d601127")

# --- Email Settings ---
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "shaikabraar6009@gmail.com")
SENDER_APP_PASSWORD = os.environ.get("SENDER_APP_PASSWORD", "goqq dxns dizu grew")

# --- Database ---
DATABASE_NAME = "ecommerce_predictive_price_tracking_system.db"

# --- Scraping Settings ---
CHECK_INTERVAL_HOURS = 6
PRICE_DROP_ALERT_PERCENTAGE = 20

# --- Sites To Scrape ---
SITES = ["amazon", "flipkart", "nykaa"]