# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Scraper File — ScraperAPI Only
# =============================================

import requests
from bs4 import BeautifulSoup
from config import SCRAPER_API_KEY
import re
import concurrent.futures

def scraper_get(url, render=False):
    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}&country_code=in"
    if render:
        api_url += "&render=true"
    response = requests.get(api_url, timeout=40)
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

        for item in items[:5]:
            try:
                # Get full product name from h2 span
                full_name = None
                h2 = item.find("h2")
                if h2:
                    span = h2.find("span")
                    full_name = span.text.strip() if span else h2.text.strip()

                if not full_name or len(full_name) < 5:
                    continue

                price_el = (
                    item.find("span", {"class": "a-price-whole"}) or
                    item.find("span", {"class": "a-offscreen"})
                )
                link_el = item.find("a", {"class": "a-link-normal"})

                if full_name and price_el and link_el:
                    price_value = extract_price(price_el.text)
                    if price_value and price_value > 0:
                        results.append({
                            "name": full_name,
                            "price": price_value,
                            "url": "https://www.amazon.in" + link_el["href"],
                            "site": "Amazon"
                        })
            except:
                continue

        return results

    except Exception as e:
        print(f"Amazon search error: {e}")
        return []

def scrape_flipkart(product_name):
    try:
        search_url = f"https://www.flipkart.com/search?q={product_name.replace(' ', '+')}"
        print(f"Searching Flipkart: {search_url}")
        # Use render=True for Flipkart to handle JavaScript
        response = scraper_get(search_url, render=True)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        # Try all known container classes
        containers = (
            soup.find_all("div", {"class": "_1AtVbE"}) or
            soup.find_all("div", {"class": "tUxRFH"}) or
            soup.find_all("div", {"class": "DOjaWF"}) or
            soup.find_all("div", {"class": "_2kHMtA"}) or
            soup.find_all("div", {"class": "yKfJKb"}) or
            soup.find_all("div", {"class": "cPHDOP"})
        )

        print(f"Flipkart containers found: {len(containers)}")

        for item in containers[:5]:
            try:
                # Try all name classes
                name_el = (
                    item.find("div", {"class": "_4rR01T"}) or
                    item.find("a", {"class": "s1Q9rs"}) or
                    item.find("div", {"class": "KzDlHZ"}) or
                    item.find("a", {"class": "IRpwTa"}) or
                    item.find("div", {"class": "fMghEO"}) or
                    item.find("div", {"class": "col col-7-12"}) or
                    item.find("a", {"class": "wjcEIp"})
                )

                if not name_el or len(name_el.text.strip()) < 3:
                    continue

                full_name = name_el.text.strip()

                price_el = (
                    item.find("div", {"class": "_30jeq3"}) or
                    item.find("div", {"class": "Nx9bqj"}) or
                    item.find("div", {"class": "hl05eU"}) or
                    item.find("div", {"class": "CEmiEU"}) or
                    item.find("div", {"class": "UOCQB1"}) or
                    item.find("div", {"class": "yRaY8j"}) or
                    item.find("div", {"class": "_25b18c"})
                )

                link_el = (
                    item.find("a", {"class": "_1fQZEK"}) or
                    item.find("a", {"class": "CGtC98"}) or
                    item.find("a", {"class": "wjcEIp"}) or
                    item.find("a", href=True)
                )

                if full_name and price_el and link_el:
                    price_value = extract_price(price_el.text)
                    if price_value and price_value > 0:
                        results.append({
                            "name": full_name,
                            "price": price_value,
                            "url": "https://www.flipkart.com" + link_el["href"],
                            "site": "Flipkart"
                        })
            except:
                continue

        return results

    except Exception as e:
        print(f"Flipkart search error: {e}")
        return []

def scrape_nykaa(product_name):
    try:
        search_url = f"https://www.nykaa.com/search/result/?q={product_name.replace(' ', '%20')}"
        print(f"Searching Nykaa: {search_url}")
        # Use render=True for Nykaa to handle JavaScript
        response = scraper_get(search_url, render=True)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        containers = (
            soup.find_all("div", {"class": "css-d0rqwe"}) or
            soup.find_all("div", {"class": "product-list"}) or
            soup.find_all("div", {"class": "css-1qsxjza"}) or
            soup.find_all("div", {"class": "css-6bz9ue"}) or
            soup.find_all("div", {"class": "css-7lncqf"}) or
            soup.find_all("li", {"class": "css-7lncqf"})
        )

        print(f"Nykaa containers found: {len(containers)}")

        for item in containers[:5]:
            try:
                name_el = (
                    item.find("div", {"class": "css-xrzmfa"}) or
                    item.find("div", {"class": "product-name"}) or
                    item.find("p", {"class": "css-1liqaa7"}) or
                    item.find("div", {"class": "css-1qtp6nl"}) or
                    item.find("div", {"class": "css-1p77ob0"}) or
                    item.find("p", {"class": "css-0"})
                )

                if not name_el or len(name_el.text.strip()) < 3:
                    continue

                full_name = name_el.text.strip()

                price_el = (
                    item.find("span", {"class": "css-111z9ua"}) or
                    item.find("span", {"class": "post-card__offer-price"}) or
                    item.find("span", {"class": "css-1jczs19"}) or
                    item.find("div", {"class": "css-1lzine0"}) or
                    item.find("span", {"class": "css-1p77ob0"})
                )

                link_el = item.find("a", href=True)

                if full_name and price_el and link_el:
                    price_value = extract_price(price_el.text)
                    if price_value and price_value > 0:
                        results.append({
                            "name": full_name,
                            "price": price_value,
                            "url": "https://www.nykaa.com" + link_el["href"],
                            "site": "Nykaa"
                        })
            except:
                continue

        return results

    except Exception as e:
        print(f"Nykaa search error: {e}")
        return []

def compare_prices(product_name):
    print(f"\nSearching for: {product_name}")
    print("=" * 50)

    amazon_results = []
    flipkart_results = []
    nykaa_results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        amazon_future = executor.submit(scrape_amazon, product_name)
        flipkart_future = executor.submit(scrape_flipkart, product_name)
        nykaa_future = executor.submit(scrape_nykaa, product_name)

        try:
            amazon_results = amazon_future.result(timeout=45)
        except:
            print("Amazon timeout")

        try:
            flipkart_results = flipkart_future.result(timeout=45)
        except:
            print("Flipkart timeout")

        try:
            nykaa_results = nykaa_future.result(timeout=45)
        except:
            print("Nykaa timeout")

    return {
        "amazon": amazon_results,
        "flipkart": flipkart_results,
        "nykaa": nykaa_results
    }

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

        if name_el and price_el:
            price_value = extract_price(price_el.text)
            if price_value:
                return {"name": name_el.text.strip(), "price": price_value, "url": clean, "site": "Amazon", "best": True}

        price_value = find_any_price(soup)
        if name_el and price_value:
            return {"name": name_el.text.strip(), "price": price_value, "url": clean, "site": "Amazon", "best": True}
        return None

    except Exception as e:
        print(f"Amazon URL error: {e}")
        return None

def scrape_flipkart_url(url):
    try:
        clean = clean_url(url, "flipkart")
        print(f"Flipkart direct URL: {clean}")
        response = scraper_get(clean, render=True)
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

        if name_el and price_el:
            price_value = extract_price(price_el.text)
            if price_value:
                return {"name": name_el.text.strip(), "price": price_value, "url": clean, "site": "Flipkart", "best": True}

        price_value = find_any_price(soup)
        if name_el and price_value:
            return {"name": name_el.text.strip(), "price": price_value, "url": clean, "site": "Flipkart", "best": True}
        return None

    except Exception as e:
        print(f"Flipkart URL error: {e}")
        return None

def scrape_nykaa_url(url):
    try:
        clean = clean_url(url, "nykaa")
        print(f"Nykaa direct URL: {clean}")
        response = scraper_get(clean, render=True)
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

        if name_el and price_el:
            price_value = extract_price(price_el.text)
            if price_value:
                return {"name": name_el.text.strip(), "price": price_value, "url": clean, "site": "Nykaa", "best": True}

        price_value = find_any_price(soup)
        if name_el and price_value:
            return {"name": name_el.text.strip(), "price": price_value, "url": clean, "site": "Nykaa", "best": True}
        return None

    except Exception as e:
        print(f"Nykaa URL error: {e}")
        return None