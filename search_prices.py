
import json
import os
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
    "download-code", "download code", "digital code",
    "eshop", "e-shop", "game key", "download",
    "digital version"
]

# FEHLENDE LISTE ERGÄNZT
PHYSICAL = [
    "spielkarte", "game card", "cartridge",
    "physisch", "physical", "at-pegi"
]


# =================================
# KATEGORIE ERMITTELN
# =================================

def category(title):

    t = title.lower()

    if any(word in t for word in EXCLUDED):
        return None

    if any(word in t for word in DIGITAL):
        return "digital"

    if any(word in t for word in PHYSICAL):
        return "physical"

    return "unknown"


# =================================
# HÄNDLERLINK PRÜFEN
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
# 1. GOOGLE SHOPPING SUCHEN
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

shopping = response.json().get("shopping_results", [])

print("Shopping-Ergebnisse:", len(shopping))


# =================================
# 2. PRODUKTSEITEN SAMMELN
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
# 3. HÄNDLERANGEBOTE ABRUFEN
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
        
        print("DEBUG Produkt:", product.get("title"))
        print("DEBUG Produktdaten:", list(product.keys()))
        print("DEBUG Händleranzahl:", len(stores))

     for s in stores[:5]:
    print("DEBUG Händler:", s)


        # WICHTIG: Diese Schleife gehört in den try-Block
        for store in stores:

            store_title = store.get("title") or ""

            product_title = (
                product.get("title")
                or products[product_id]
            )

            # Beide Titel prüfen
            combined_title = store_title + " " + product_title

            if "pokopia" not in combined_title.lower():
                continue

            kind = category(combined_title)

            if kind is None:
                print("AUSGESCHLOSSEN:", combined_title)
                continue

            price = store.get("extracted_price")

            link = store.get("link")

            if price is None:
                continue

            if not valid_store_link(link):
                continue

            try:
                price = float(price)
            except (ValueError, TypeError):
                continue

            if price <= 0:
                continue

            merchant = store.get("name") or "Unbekannt"

            # Doppelte Angebote vermeiden
            unique_id = (merchant.lower(), link, kind)

            if unique_id in seen:
                continue

            seen.add(unique_id)

            offer = {
                "title": store_title or product_title,
                "price": round(price, 2),
                "currency": "EUR",
                "merchant": merchant,
                "url": link,
                "type": kind,
                "delivery": store.get("shipping", "")
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
            "Fehler bei Produkt",
            product_id,
            error
        )


# =================================
# 4. PREISE SORTIEREN
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
# 5. ERGEBNIS SPEICHERN
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
# 6. AUSGABE
# =================================

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

    print("NICHT EINDEUTIG ZUGEORDNETE ANGEBOTE:")

    for offer in unknown:
        print(
            offer["merchant"],
            offer["price"],
            "Euro"
        )

print("--------------------------------")

print("POKOPIA DEAL FINDER FERTIG")
