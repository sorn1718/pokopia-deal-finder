
import json
import os
import re
import requests
from datetime import datetime, timezone
from urllib.parse import urlparse

API_KEY = os.environ["SERPAPI_API_KEY"]
BASE = "https://serpapi.com/search.json"

QUERY = "Pokémon Pokopia Nintendo Switch 2 kaufen"

EXCLUDED = [
    "erweiterungspass", "expansion pass", "skin",
    "cover", "vinyl", "hülle", "case",
    "schlüsselanhänger", "keychain", "controller",
    "tasche", "schutzfolie", "sticker", "figur",
    "plüschtier", "poster", "soundtrack",
    "bundle", "konsole", "console", "joycon",
    "merchandise", "zubehör", "accessory",
    "lösungsbuch", "guide"
]

DIGITAL = [
    "download-code", "download code",
    "digital code", "eshop", "e-shop",
    "game key", "digital version",
    "download version"
]

PHYSICAL = [
    "spielkarte", "game card", "cartridge",
    "physisch", "physical", "at-pegi",
    "switch2-spiel", "switch 2 spiel",
    "nintendo switch 2 spiel",
    "nintendo switch 2 game"
]


# =================================
# 1. KATEGORIE ERMITTELN
# =================================

def category(store_title, product_title=""):

    store = store_title.lower()
    product = product_title.lower()

    if any(word in store for word in EXCLUDED):
        return None

    # Zuerst den eigentlichen Händlertitel prüfen
    if any(word in store for word in DIGITAL):
        return "digital"

    if any(word in store for word in PHYSICAL):
        return "physical"

    # Produkttitel nur als zusätzliche Information
    if any(word in product for word in DIGITAL):
        return "digital"

    if any(word in product for word in PHYSICAL):
        return "physical"

    # Switch-2-Spiel ohne Digital-Kennzeichnung
    if (
        "switch 2" in store
        or "switch2" in store
    ):
        return "physical"

    return "unknown"


# =================================
# 2. HÄNDLERLINK PRÜFEN
# =================================

def valid_store_link(link):

    if not link:
        return False

    try:
        parsed = urlparse(link)

        return (
            parsed.scheme == "https"
            and parsed.hostname is not None
            and "google." not in parsed.hostname
            and "serpapi.com" not in parsed.hostname
        )

    except Exception:
        return False


# =================================
# 3. PREIS ERMITTELN
# =================================

def get_price(store):

    total = store.get("extracted_total")

    price = store.get("extracted_price")

    # Gesamtpreis inklusive Versand bevorzugen
    if total is not None:
        try:
            return round(float(total), 2)
        except (ValueError, TypeError):
            pass

    if price is not None:
        try:
            return round(float(price), 2)
        except (ValueError, TypeError):
            return None

    return None


# =================================
# 4. GOOGLE SHOPPING SUCHEN
# =================================

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

shopping_data = response.json()

shopping = shopping_data.get("shopping_results", [])

print("Shopping-Ergebnisse:", len(shopping))


# =================================
# 5. PRODUKTSEITEN SAMMELN
# =================================

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


product_ids = list(products.keys())[:4]

print("Produktseiten:", len(product_ids))


# =================================
# 6. HÄNDLERANGEBOTE ABRUFEN
# =================================

offers = []
seen = set()

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

        product_title = (
            product.get("title")
            or products[product_id]
        )

        print("--------------------------------")
        print("DEBUG PRODUKT:", product_title)
        print("DEBUG HÄNDLERANZAHL:", len(stores))

        for store in stores:

            store_title = (
                store.get("title")
                or product_title
            )

            kind = category(store_title, product_title)

            if kind is None:
                print("AUSGESCHLOSSEN:", store_title)
                continue

            price = get_price(store)

            if price is None or price <= 0:
                continue

            link = store.get("link")

            if not valid_store_link(link):
                print("UNGÜLTIGER LINK:", store_title)
                continue

            merchant = store.get("name") or "Unbekannt"

            unique_id = (
                merchant.lower(),
                link,
                kind
            )

            if unique_id in seen:
                continue

            seen.add(unique_id)

            offer = {
                "title": store_title,
                "price": price,
                "currency": "EUR",
                "merchant": merchant,
                "url": link,
                "type": kind,
                "delivery": store.get("shipping", ""),
                "item_price": store.get("extracted_price"),
                "total_price": store.get("extracted_total")
            }

            offers.append(offer)

            print(
                "ANGEBOT:",
                kind,
                merchant,
                price,
                "Euro"
            )

    except Exception as error:

        print(
            "FEHLER BEI PRODUKT:",
            product_id,
            error
        )


# =================================
# 7. PREISE SORTIEREN
# =================================

offers.sort(key=lambda x: x["price"])

physical = [
    o for o in offers
    if o["type"] == "physical"
]

digital = [
    o for o in offers
    if o["type"] == "digital"
]

unknown = [
    o for o in offers
    if o["type"] == "unknown"
]


# =================================
# 8. ERGEBNIS SPEICHERN
# =================================

data = {
    "product": "Pokémon Pokopia Nintendo Switch 2",

    "checked_at": datetime.now(
        timezone.utc
    ).isoformat(),

    "offers": offers,

    "best_price": (
        offers[0]["price"]
        if offers else None
    ),

    "physical_best": (
        physical[0]["price"]
        if physical else None
    ),

    "digital_best": (
        digital[0]["price"]
        if digital else None
    ),

    "unknown_best": (
        unknown[0]["price"]
        if unknown else None
    ),

    "physical_offers": physical,
    "digital_offers": digital,
    "unknown_offers": unknown
}


with open("offers.json", "w", encoding="utf-8") as file:

    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )


# =================================
# 9. ERGEBNIS AUSGEBEN
# =================================

print("--------------------------------")
print("POKOPIA DEAL FINDER")
print("--------------------------------")

print("GESAMTANGEBOTE:", len(offers))
print("PHYSISCH:", len(physical))
print("DIGITAL:", len(digital))
print("UNKLAR:", len(unknown))

if physical:
    print(
        "BESTER PHYSISCHER PREIS:",
        physical[0]["price"],
        "Euro"
    )

if digital:
    print(
        "BESTER DIGITALER PREIS:",
        digital[0]["price"],
        "Euro"
    )

if unknown:
    print(
        "BESTER UNKLARER PREIS:",
        unknown[0]["price"],
        "Euro"
    )

print("--------------------------------")
print("offers.json ERFOLGREICH GESPEICHERT")
print("POKOPIA DEAL FINDER FERTIG")
