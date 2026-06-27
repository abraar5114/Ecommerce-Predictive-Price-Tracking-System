# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Scraper File — URL-based tracking only
# (Search-by-name removed: unreliable across sites,
#  caused mismatched products and Render memory crashes)
# =============================================

import requests
from bs4 import BeautifulSoup
from config import SCRAPER_API_KEY
import re


def scraper_get(url, timeout=40):
    """Single sequential request through ScraperAPI. No render=True (too heavy for free tier)."""
    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}&country_code=in"
    return requests.get(api_url, timeout=timeout)


def extract_price(text):
    try:
        cleaned = re.sub(r'[₹,\s]', '', text)
        match = re.search(r'\d+\.?\d*', cleaned)
        if match:
            return float(match.group())
        return None
    except Exception:
        return None


def clean_url(url, site):
    try:
        if site == "flipkart":
            return url.split("?")[0]
        elif site == "amazon":
            if "/dp/" in url:
                base = url.split("/dp/")[0]
                dp = url.split("/dp/")[1].split("/")[0].split("?")[0]
                return f"{base}/dp/{dp}"
            return url.split("?")[0]
        elif site == "nykaa":
            return url.split("?")[0]
        return url
    except Exception:
        return url


def find_any_price(soup):
    """Fallback: scan the page for anything that looks like a rupee price."""
    for tag in soup.find_all(["span", "div", "strong", "p"]):
        text = tag.text.strip()
        if "₹" in text and len(text) < 20:
            price = extract_price(text)
            if price and price > 10:
                return price
    return None


def detect_site(url):
    if "amazon" in url:
        return "Amazon"
    elif "flipkart" in url:
        return "Flipkart"
    elif "nykaa" in url:
        return "Nykaa"
    return None


# =============================================
# DIRECT URL SCRAPING
# =============================================

def scrape_direct_url(url):
    site = detect_site(url)
    if site == "Amazon":
        return scrape_amazon_url(url)
    elif site == "Flipkart":
        return scrape_flipkart_url(url)
    elif site == "Nykaa":
        return scrape_nykaa_url(url)
    return None


def scrape_amazon_url(url):
    try:
        clean = clean_url(url, "amazon")
        print(f"Amazon URL: {clean}")
        response = scraper_get(clean)
        soup = BeautifulSoup(response.text, "html.parser")

        name_el = (
            soup.find("span", {"id": "productTitle"}) or
            soup.find("h1", {"id": "title"})
        )
        price_el = (
            soup.find("span", {"class": "a-price-whole"}) or
            soup.find("span", {"id": "priceblock_ourprice"}) or
            soup.find("span", {"id": "priceblock_dealprice"}) or
            soup.find("span", {"class": "a-offscreen"})
        )

        price_value = extract_price(price_el.text) if price_el else None
        if not price_value:
            price_value = find_any_price(soup)

        print(f"Amazon name: {name_el.text.strip() if name_el else 'NOT FOUND'}")
        print(f"Amazon price: {price_value}")

        if name_el and price_value:
            return {
                "name": name_el.text.strip()[:200],
                "price": price_value,
                "url": clean,
                "site": "Amazon"
            }
        return None

    except Exception as e:
        print(f"Amazon URL error: {e}")
        return None


def scrape_flipkart_url(url):
    try:
        clean = clean_url(url, "flipkart")
        print(f"Flipkart URL: {clean}")
        response = scraper_get(clean)
        soup = BeautifulSoup(response.text, "html.parser")

        name_el = (
            soup.find("span", {"class": "B_NuCI"}) or
            soup.find("h1", {"class": "yhB1nd"}) or
            soup.find("span", {"class": "VU-ZEz"}) or
            soup.find("span", {"class": "mEh187"}) or
            soup.find("h1")
        )
        price_el = (
            soup.find("div", {"class": "_30jeq3"}) or
            soup.find("div", {"class": "Nx9bqj"}) or
            soup.find("div", {"class": "hl05eU"}) or
            soup.find("div", {"class": "CEmiEU"}) or
            soup.find("div", {"class": "UOCQB1"}) or
            soup.find("div", {"class": "yRaY8j"}) or
            soup.find("div", {"class": "CxhGGd"})
        )

        price_value = extract_price(price_el.text) if price_el else None
        if not price_value:
            price_value = find_any_price(soup)

        print(f"Flipkart name: {name_el.text.strip() if name_el else 'NOT FOUND'}")
        print(f"Flipkart price: {price_value}")

        if name_el and price_value:
            return {
                "name": name_el.text.strip()[:200],
                "price": price_value,
                "url": clean,
                "site": "Flipkart"
            }
        return None

    except Exception as e:
        print(f"Flipkart URL error: {e}")
        return None


def scrape_nykaa_url(url):
    try:
        clean = clean_url(url, "nykaa")
        print(f"Nykaa URL: {clean}")
        response = scraper_get(clean)
        soup = BeautifulSoup(response.text, "html.parser")

        name_el = (
            soup.find("h1", {"class": "css-1gc4x7i"}) or
            soup.find("h1", {"class": "product-name"}) or
            soup.find("h1", {"class": "css-r0zjzh"}) or
            soup.find("h1")
        )
        price_el = (
            soup.find("span", {"class": "css-111z9ua"}) or
            soup.find("span", {"class": "post-card__offer-price"}) or
            soup.find("span", {"class": "css-1jczs19"}) or
            soup.find("div", {"class": "css-1lzine0"})
        )

        price_value = extract_price(price_el.text) if price_el else None
        if not price_value:
            price_value = find_any_price(soup)

        print(f"Nykaa name: {name_el.text.strip() if name_el else 'NOT FOUND'}")
        print(f"Nykaa price: {price_value}")

        if name_el and price_value:
            return {
                "name": name_el.text.strip()[:200],
                "price": price_value,
                "url": clean,
                "site": "Nykaa"
            }
        return None

    except Exception as e:
        print(f"Nykaa URL error: {e}")
        return None


def check_price(product):
    """Used by the scheduler to re-check price of an already-tracked product."""
    url = product[2]
    site = product[3]
    try:
        if site == "Amazon":
            result = scrape_amazon_url(url)
        elif site == "Flipkart":
            result = scrape_flipkart_url(url)
        elif site == "Nykaa":
            result = scrape_nykaa_url(url)
        else:
            result = None
        return result["price"] if result else None
    except Exception as e:
        print(f"check_price error: {e}")
        return None