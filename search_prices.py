
import json
import os
import re
import requests
from datetime import datetime, timezone

API_KEY = os.environ["SERPAPI_API_KEY"]
QUERY = "Pokémon Pokopia Nintendo Switch 2 kaufen"

response = requests.get(
    "https://serpapi.com/search.json",
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
results = response.json().get("shopping_results", [])

offers = []

for item in results:
    title = item.get("title", "")
    if "pokopia" not in title.lower():
        continue

    price = item.get("extracted_price")
    link = item.get("link")

    if price is None or not link:
        continue

    offers.append({
        "title": title,
        "price": float(price),
        "currency": "EUR",
        "merchant": item.get("source", "Unbekannt"),
        "url": link,
        "delivery": item.get("delivery"),
        "thumbnail": item.get("thumbnail")
    })

offers.sort(key=lambda x: x["price"])

data = {
    "product": "Pokémon Pokopia für Nintendo Switch 2",
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "offers": offers,
    "best_price": offers[0]["price"] if offers else None
}

with open("offers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Gefundene Angebote:", len(offers))
