
import json
import os
import requests
from datetime import datetime, timezone

API_KEY = os.environ["SERPAPI_API_KEY"]

QUERY = "Pokémon Pokopia Nintendo Switch 2 Spiel kaufen"

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

offers = []

# Zubehör ausschließen
excluded = [
    "skin", "cover", "vinyl", "wrap",
    "hülle", "case", "schlüsselanhänger",
    "keychain", "controller", "tasche",
    "schutzfolie", "sticker", "figur",
    "plüschtier", "poster", "soundtrack"
]

for item in shopping:

    title = item.get("title", "")
    normalized = title.lower()

    if "pokopia" not in normalized:
        continue

    if any(word in normalized for word in excluded):
        print("Zubehör ausgeschlossen:", title)
        continue

    # Beide möglichen Link-Felder prüfen
    link = item.get("product_link") or item.get("link")

    price = item.get("extracted_price")

    if price is None:
        print("Preis fehlt:", title)
        continue

    if not link:
        print("Händlerlink fehlt:", title)
        continue

    offer = {
        "title": title,
        "price": float(price),
        "currency": "EUR",
        "merchant": item.get("source", "Unbekannt"),
        "url": link,
        "delivery": item.get("delivery"),
        "thumbnail": item.get("thumbnail")
    }

    offers.append(offer)

    print("ANGEBOT GEFUNDEN:", title, price, "Euro")

# Nach Preis sortieren
offers.sort(key=lambda x: x["price"])

data = {
    "product": "Pokémon Pokopia für Nintendo Switch 2",
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "offers": offers,
    "best_price": offers[0]["price"] if offers else None
}

with open("offers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("--------------------------------")
print("Gefundene Pokopia-Angebote:", len(offers))

if offers:
    print("GÜNSTIGSTER PREIS:", offers[0]["price"], "Euro")
    print("HÄNDLER:", offers[0]["merchant"])
    print("LINK:", offers[0]["url"])
else:
    print("Noch keine passenden Angebote gefunden.")
    print("SerpApi Status:",
          result.get("search_metadata", {}).get("status"))
