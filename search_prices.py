
import json
import os
import requests
from datetime import datetime, timezone

API_KEY = os.environ["SERPAPI_API_KEY"]
BASE = "https://serpapi.com/search.json"

QUERY = "Pokémon Pokopia Nintendo Switch 2 Spiel kaufen"

EXCLUDED = [
    "erweiterungspass", "expansion pass", "skin", "cover",
    "vinyl", "hülle", "case", "schlüsselanhänger",
    "keychain", "controller", "tasche", "schutzfolie",
    "sticker", "figur", "plüschtier", "poster",
    "soundtrack", "bundle", "konsole", "console",
    "joycon", "merchandise", "zubehör", "accessory",
    "lösungsbuch", "guide"
]

DIGITAL = [
    "download-code", "download code", "digital code",
    "eshop", "e-shop", "game key", "download"
]

PHYSICAL = [
    "spielkarte", "game card", "cartridge",
    "physisch", "physical", "at-pegi"
]

def category(title):
    t = title.lower()

    if any(word in t for word in EXCLUDED):
        return None

    if any(word in t for word in DIGITAL):
        return "digital"

    if any(word in t for word in PHYSICAL):
        return "physical"

    return None


def valid_store_link(link):
    if not link:
        return False

    link = link.lower()

    return (
        link.startswith("https://")
        and "google." not in link.split("/")[2]
        and "serpapi.com" not in link
    )


# 1. Google Shopping durchsuchen
response = requests.get(
    BASE,
    params={
        "engine": "google_shopping",
        "q": QUERY,
        "google_domain": "google.de",
        "gl": "de",
        "hl": "de",
        "api_key": API_KEY
    },
    timeout=45
)

response.raise_for_status()
shopping = response.json().get("shopping_results", [])

print("Shopping-Ergebnisse:", len(shopping))

# 2. Passende Produkt-IDs sammeln
products = {}

for item in shopping:
    title = item.get("title", "")
    
    if "pokopia" not in title.lower():
        continue

    if any(word in title.lower() for word in EXCLUDED):
        continue

    product_id = item.get("product_id")

    if product_id:
        products[product_id] = title

# Maximal vier unterschiedliche Produktseiten abfragen
product_ids = list(products.keys())[:4]

print("Produktseiten werden geprüft:", len(product_ids))

offers = []

# 3. Händlerangebote mit direkten Links abrufen
for product_id in product_ids:

    try:
        product_response = requests.get(
            BASE,
            params={
                "engine": "google_product",
                "product_id": product_id,
                "offer_view": "true",
                "gl": "de",
                "hl": "de",
                "api_key": API_KEY
            },
            timeout=45
        )

        product_response.raise_for_status()
        product_data = product_response.json()

        product = product_data.get("product_results", {})
        stores = product.get("stores", [])

        for store in stores:

            title = store.get("title") or product.get("title") or products[product_id]
            combined_title = title + " " + products[product_id]

            kind = category(combined_title)

            if kind is None:
                continue

            price = store.get("extracted_price")
            link = store.get("link")

            if price is None or not valid_store_link(link):
                continue

            offer = {
                "title": title,
                "price": float(price),
                "currency": "EUR",
                "merchant": store.get("name", "Unbekannt"),
                "url": link,
                "type": kind,
                "delivery": store.get("shipping", "")
            }

            offers.append(offer)

            print(
                "DIREKTANGEBOT:",
                offer["merchant"],
                offer["price"],
                offer["url"]
            )

    except Exception as error:
        print("Produkt konnte nicht geladen werden:", error)

# 4. Nach Preis sortieren
offers.sort(key=lambda x: x["price"])

physical = [o for o in offers if o["type"] == "physical"]
digital = [o for o in offers if o["type"] == "digital"]

data = {
    "product": "Pokémon Pokopia Nintendo Switch 2",
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "offers": offers,
    "best_price": offers[0]["price"] if offers else None,
    "physical_best": physical[0]["price"] if physical else None,
    "digital_best": digital[0]["price"] if digital else None
}

with open("offers.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print("--------------------------------")
print("Direkte Händlerangebote:", len(offers))
print("Physische Angebote:", len(physical))
print("Digitale Angebote:", len(digital))
print("--------------------------------")
