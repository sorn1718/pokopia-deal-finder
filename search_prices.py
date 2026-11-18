
import json
import os
import requests
from datetime import datetime, timezone

# =====================================
# POKOPIA DEAL FINDER
# =====================================

API_KEY = os.environ["SERPAPI_API_KEY"]

QUERY = "Pokémon Pokopia Nintendo Switch 2 Spiel kaufen"

# =====================================
# GOOGLE SHOPPING ABFRAGEN
# =====================================

response = requests.get(
    "https://serpapi.com/search.json",
    params={
        "engine": "google_shopping",
        "q": QUERY,
        "google_domain": "google.de",
        "gl": "de",
        "hl": "de",
        "location": "Germany",
        "api_key": API_KEY
    },
    timeout=45
)

response.raise_for_status()

result = response.json()

shopping = result.get("shopping_results", [])

print("Google Shopping Ergebnisse:", len(shopping))

# =====================================
# UNERWÜNSCHTE PRODUKTE
# =====================================

excluded = [
    "erweiterungspass",
    "expansion pass",
    "skin",
    "cover",
    "vinyl",
    "wrap",
    "hülle",
    "case",
    "schlüsselanhänger",
    "keychain",
    "controller",
    "tasche",
    "schutzfolie",
    "sticker",
    "figur",
    "plüschtier",
    "poster",
    "soundtrack",
    "bundle",
    "konsole",
    "console",
    "joycon",
    "merchandise",
    "zubehör",
    "accessory",
    "accessories",
    "switch 2 + pokopia-set",
    "lösungsbuch",
    "guide"
]

# =====================================
# ANGEBOTE FILTERN
# =====================================

offers = []

for item in shopping:

    title = item.get("title", "")
    normalized = title.lower()

    # Pokopia muss im Titel vorkommen
    if "pokopia" not in normalized:
        continue

    # Zubehör und Erweiterungspässe ausschließen
    if any(word in normalized for word in excluded):
        print("AUSGESCHLOSSEN:", title)
        continue

    # Preis auslesen
    price = item.get("extracted_price")

    if price is None:
        print("KEIN PREIS:", title)
        continue

    try:
        price = float(price)
    except (ValueError, TypeError):
        continue

    if price <= 0:
        continue

    # Händlerlink auslesen
    link = item.get("product_link") or item.get("link")

    if not link:
        print("KEIN LINK:", title)
        continue

    merchant = item.get("source", "Unbekannt")

    offer = {
        "title": title,
        "price": round(price, 2),
        "currency": "EUR",
        "merchant": merchant,
        "url": link,
        "delivery": item.get("delivery"),
        "thumbnail": item.get("thumbnail")
    }

    offers.append(offer)

    print(
        "ANGEBOT GEFUNDEN:",
        title,
        price,
        "Euro"
    )

# =====================================
# PREISE SORTIEREN
# =====================================

offers.sort(key=lambda x: x["price"])

# =====================================
# ERGEBNIS SPEICHERN
# =====================================

data = {
    "product": "Pokémon Pokopia für Nintendo Switch 2",
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "offers": offers,
    "best_price": offers[0]["price"] if offers else None
}

with open("offers.json", "w", encoding="utf-8") as file:
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )

# =====================================
# AUSGABE
# =====================================

print("--------------------------------")

print("Gefundene Pokopia-Angebote:", len(offers))

if offers:

    print(
        "GÜNSTIGSTER PREIS:",
        offers[0]["price"],
        "Euro"
    )

    print(
        "HÄNDLER:",
        offers[0]["merchant"]
    )

    print(
        "LINK:",
        offers[0]["url"]
    )

else:

    print("Keine passenden Angebote gefunden.")

    print(
        "SerpApi Status:",
        result.get("search_metadata", {}).get("status")
    )

print("--------------------------------")
print("Pokopia Deal Finder beendet.")
