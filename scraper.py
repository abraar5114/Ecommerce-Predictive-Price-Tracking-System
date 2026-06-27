# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Scraper File — ScraperAPI Only (No Selenium)
# =============================================

import requests
from bs4 import BeautifulSoup
from config import SCRAPER_API_KEY
import re

def scraper_get(url):
    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}&country_code=in"
    response = requests.get(api_url, timeout=30)
    return response

def extract_price(text):
    try:
        cleaned = re.sub(r'[₹,\s]', '', text)
        match = re.search(r'\d+\.?\d*', cleaned)
        if match:
            return float(match.group())
        return None
    except:
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
    except:
        return url

def find_any_price(soup):
    for tag in soup.find_all(["span", "div", "strong", "p"]):
        text = tag.text.strip()
        if "₹" in text and len(text) < 20:
            price = extract_price(text)
            if price and price > 10:
                return price
    return None

def scrape_amazon(product_name):
    try:
        search_url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
        print(f"Searching Amazon: {search_url}")
        response = scraper_get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        items = soup.find_all("div", {"data-component-type": "s-search-result"})
        print(f"Amazon items found: {len(items)}")

        for item in items[:8]:
            try:
                name_el = (
                    item.find("span", {"class": "a-size-medium"}) or
                    item.find("span", {"class": "a-size-base-plus"}) or
                    item.find("h2")
                )
                price_el = (
                    item.find("span", {"class": "a-price-whole"}) or
                    item.find("span", {"class": "a-offscreen"})
                )
                link_el = item.find("a", {"class": "a-link-normal"})

                if name_el and price_el and link_el:
                    price_value = extract_price(price_el.text)
                    if price_value and price_value > 0:
                        results.append({
                            "name": name_el.text.strip()[:100],
                            "price": price_value,
                            "url": "https://www.amazon.in" + link_el["href"],
                            "site": "Amazon"
                        })
            except:
                continue

        if results:
            best = min(results, key=lambda x: x["price"])
            print(f"Amazon best: {best['name']} — ₹{best['price']}")
            return best
        return None

    except Exception as e:
        print(f"Amazon search error: {e}")
        return None

def scrape_flipkart(product_name):
    try:
        search_url = f"https://www.flipkart.com/search?q={product_name.replace(' ', '+')}"
        print(f"Searching Flipkart: {search_url}")
        response = scraper_get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        containers = (
            soup.find_all("div", {"class": "_1AtVbE"}) or
            soup.find_all("div", {"class": "tUxRFH"}) or
            soup.find_all("div", {"class": "DOjaWF"}) or
            soup.find_all("div", {"class": "_2kHMtA"}) or
            soup.find_all("div", {"class": "yKfJKb"})
        )

        print(f"Flipkart containers found: {len(containers)}")

        for item in containers[:8]:
            try:
                name_el = (
                    item.find("div", {"class": "_4rR01T"}) or
                    item.find("a", {"class": "s1Q9rs"}) or
                    item.find("div", {"class": "KzDlHZ"}) or
                    item.find("a", {"class": "IRpwTa"}) or
                    item.find("div", {"class": "fMghEO"})
                )
                price_el = (
                    item.find("div", {"class": "_30jeq3"}) or
                    item.find("div", {"class": "Nx9bqj"}) or
                    item.find("div", {"class": "hl05eU"}) or
                    item.find("div", {"class": "CEmiEU"}) or
                    item.find("div", {"class": "UOCQB1"}) or
                    item.find("div", {"class": "yRaY8j"})
                )
                link_el = (
                    item.find("a", {"class": "_1fQZEK"}) or
                    item.find("a", {"class": "CGtC98"}) or
                    item.find("a", href=True)
                )
                if name_el and price_el and link_el:
                    price_value = extract_price(price_el.text)
                    if price_value and price_value > 0:
                        results.append({
                            "name": name_el.text.strip()[:100],
                            "price": price_value,
                            "url": "https://www.flipkart.com" + link_el["href"],
                            "site": "Flipkart"
                        })
            except:
                continue

        if results:
            best = min(results, key=lambda x: x["price"])
            print(f"Flipkart best: {best['name']} — ₹{best['price']}")
            return best
        return None

    except Exception as e:
        print(f"Flipkart search error: {e}")
        return None

def scrape_nykaa(product_name):
    try:
        search_url = f"https://www.nykaa.com/search/result/?q={product_name.replace(' ', '%20')}"
        print(f"Searching Nykaa: {search_url}")
        response = scraper_get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        containers = (
            soup.find_all("div", {"class": "css-d0rqwe"}) or
            soup.find_all("div", {"class": "product-list"}) or
            soup.find_all("div", {"class": "css-1qsxjza"}) or
            soup.find_all("div", {"class": "css-6bz9ue"})
        )

        print(f"Nykaa containers found: {len(containers)}")

        for item in containers[:8]:
            try:
                name_el = (
                    item.find("div", {"class": "css-xrzmfa"}) or
                    item.find("div", {"class": "product-name"}) or
                    item.find("p", {"class": "css-1liqaa7"})
                )
                price_el = (
                    item.find("span", {"class": "css-111z9ua"}) or
                    item.find("span", {"class": "post-card__offer-price"}) or
                    item.find("span", {"class": "css-1jczs19"})
                )
                link_el = item.find("a", href=True)

                if name_el and price_el and link_el:
                    price_value = extract_price(price_el.text)
                    if price_value and price_value > 0:
                        results.append({
                            "name": name_el.text.strip()[:100],
                            "price": price_value,
                            "url": "https://www.nykaa.com" + link_el["href"],
                            "site": "Nykaa"
                        })
            except:
                continue

        if results:
            best = min(results, key=lambda x: x["price"])
            print(f"Nykaa best: {best['name']} — ₹{best['price']}")
            return best
        return None

    except Exception as e:
        print(f"Nykaa search error: {e}")
        return None

def compare_prices(product_name):
    print(f"\nSearching for: {product_name}")

    results = []

    # Try Amazon first
    try:
        amazon_result = scrape_amazon(product_name)
        if amazon_result:
            results.append(amazon_result)
    except:
        pass

    # Try Flipkart
    try:
        flipkart_result = scrape_flipkart(product_name)
        if flipkart_result:
            results.append(flipkart_result)
    except:
        pass

    # Try Nykaa
    try:
        nykaa_result = scrape_nykaa(product_name)
        if nykaa_result:
            results.append(nykaa_result)
    except:
        pass

    if not results:
        return None

    results.sort(key=lambda x: x["price"])
    results[0]["best"] = True
    for r in results[1:]:
        r["best"] = False

    return results

def scrape_direct_url(url):
    try:
        if "amazon" in url:
            return scrape_amazon_url(url)
        elif "flipkart" in url:
            return scrape_flipkart_url(url)
        elif "nykaa" in url:
            return scrape_nykaa_url(url)
        else:
            return None
    except Exception as e:
        print(f"Direct URL error: {e}")
        return None

def scrape_amazon_url(url):
    try:
        clean = clean_url(url, "amazon")
        print(f"Amazon direct URL: {clean}")
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

        print(f"Amazon name: {name_el.text.strip() if name_el else 'NOT FOUND'}")
        print(f"Amazon price: {price_el.text.strip() if price_el else 'NOT FOUND'}")

        if name_el and price_el:
            price_value = extract_price(price_el.text)
            if price_value:
                return {"name": name_el.text.strip()[:100], "price": price_value, "url": clean, "site": "Amazon", "best": True}

        price_value = find_any_price(soup)
        if name_el and price_value:
            return {"name": name_el.text.strip()[:100], "price": price_value, "url": clean, "site": "Amazon", "best": True}
        return None

    except Exception as e:
        print(f"Amazon URL error: {e}")
        return None

def scrape_flipkart_url(url):
    try:
        clean = clean_url(url, "flipkart")
        print(f"Flipkart direct URL: {clean}")
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

        print(f"Flipkart name: {name_el.text.strip() if name_el else 'NOT FOUND'}")
        print(f"Flipkart price: {price_el.text.strip() if price_el else 'NOT FOUND'}")

        if name_el and price_el:
            price_value = extract_price(price_el.text)
            if price_value:
                return {"name": name_el.text.strip()[:100], "price": price_value, "url": clean, "site": "Flipkart", "best": True}

        price_value = find_any_price(soup)
        if name_el and price_value:
            return {"name": name_el.text.strip()[:100], "price": price_value, "url": clean, "site": "Flipkart", "best": True}
        return None

    except Exception as e:
        print(f"Flipkart URL error: {e}")
        return None

def scrape_nykaa_url(url):
    try:
        clean = clean_url(url, "nykaa")
        print(f"Nykaa direct URL: {clean}")
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

        print(f"Nykaa name: {name_el.text.strip() if name_el else 'NOT FOUND'}")
        print(f"Nykaa price: {price_el.text.strip() if price_el else 'NOT FOUND'}")

        if name_el and price_el:
            price_value = extract_price(price_el.text)
            if price_value:
                return {"name": name_el.text.strip()[:100], "price": price_value, "url": clean, "site": "Nykaa", "best": True}

        price_value = find_any_price(soup)
        if name_el and price_value:
            return {"name": name_el.text.strip()[:100], "price": price_value, "url": clean, "site": "Nykaa", "best": True}
        return None

    except Exception as e:
        print(f"Nykaa URL error: {e}")
        return None
    