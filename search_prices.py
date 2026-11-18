
import json
import os
import re
import requests
from datetime import datetime, timezone

API_KEY = os.environ["SERPAPI_API_KEY"]
QUERY = "Pokopia"

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
for i, item in enumerate(shopping[:15], 1):
    print(
        "ERGEBNIS", i,
        "TITEL:", repr(item.get("title")),
        "PREIS:", item.get("price"),
        "HÄNDLER:", item.get("source")
    )
offers = []

for item in shopping:
    title = item.get("title", "")
    
    if "pokopia" not in title.lower():
        continue

    price = item.get("extracted_price")

    if price is None:
        raw = str(item.get("price", ""))
        match = re.search(r"(\d[\d.,]*)", raw)

        if match:
            value = match.group(1)
            if "," in value:
                value = value.replace(".", "").replace(",", ".")
            try:
                price = float(value)
            except ValueError:
                continue

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
    "product": "Pokémon Pokopia Nintendo Switch 2",
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "offers": offers,
    "best_price": offers[0]["price"] if offers else None
}

with open("offers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Gefundene Pokopia-Angebote:", len(offers))

if offers:
    print("Bester Preis:", offers[0]["price"], "Euro")
else:
    print("Keine passenden Angebote gefunden.")
    print("SerpApi Antwort:", result.get("search_metadata", {}).get("status"))
