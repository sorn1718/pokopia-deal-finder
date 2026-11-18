# Pokopia Deal-Finder – iPhone Web-App

1. Lade alle Dateien aus diesem ZIP in den **Hauptordner** deines bestehenden Repositorys `pokopia-deal-finder`. Behalte `offers.json`, `search_prices.py` und `.github/` unbedingt bei.
2. GitHub → Repository → Settings → Pages.
3. Bei Build and deployment: Source **Deploy from a branch**, Branch `main`, Ordner `/ (root)`, dann Save.
4. Warte auf die veröffentlichte Pages-Adresse. Sie steht unter Settings → Pages.
5. Öffne diese Adresse in Safari auf dem iPhone → Teilen → Zum Home-Bildschirm → Hinzufügen.

Die App lädt `./offers.json` aus demselben Repository. Du musst keine URL im Code ändern.

Kategorisierung:
- Digital: Titel enthält z.B. Download-Code, digital code, eShop, game key.
- Physisch: Titel enthält z.B. Spielkarte, game card, cartridge, physical oder AT-PEGI.
- Unklare Titel werden nicht stillschweigend einer Kategorie zugeordnet.

Der Button Aktualisieren lädt nur die zuletzt gespeicherten Daten neu. Der tägliche Suchlauf wird weiterhin von GitHub Actions ausgeführt. Echte Push-Nachrichten benötigen einen zusätzlichen Push-Dienst. Bei öffentlichem Repository sind auch offers.json und die Website öffentlich. Niemals API-Schlüssel in die Web-App eintragen. Preise und Produktzuordnung vor dem Kauf beim Händler prüfen.
