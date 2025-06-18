import asyncio
from playwright.async_api import async_playwright
import argparse
import csv
from datetime import datetime
import time

async def lade_messwert(messstellen_id, timeout, debug):
    url = f"https://odlinfo.bfs.de/ODL/DE/themen/wo-stehen-die-sonden/karte/_documents/Messstelle.html?id={messstellen_id}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        if debug:
            print(f"🌐 Lade URL: {url}")
            print(f"⏳ Timeout: {timeout} Sekunden")

        await page.goto(url)

        try:
            await page.wait_for_selector("p.aktmw > strong.js-decimal:not(:empty)", timeout=timeout * 1000)
            element = await page.query_selector("p.aktmw > strong.js-decimal")
            messwert = await element.inner_text()
            return messwert.strip()
        except Exception as e:
            if debug:
                print(f"❌ Kein Messwert gefunden: {e}")
            return None
        finally:
            await browser.close()

async def main():
    parser = argparse.ArgumentParser(description="ODLinfo Messwert Ausleser")
    parser.add_argument("--id", required=True, help="Messstellen-ID")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in Sekunden (Default: 30)")
    parser.add_argument("--interval", type=int, default=5, help="Wiederholungsintervall in Minuten (Default: 5)")
    parser.add_argument("--csv", help="CSV-Datei (Standard: messwerte_YYYY-MM-DD.csv)")
    parser.add_argument("--debug", action="store_true", help="Debug-Ausgaben anzeigen")
    args = parser.parse_args()

    heute = datetime.now().strftime("%Y-%m-%d")
    csv_datei = args.csv or f"messwerte_{heute}.csv"

    print(f"⏱️ Starte wiederholte Messung für ID {args.id} – Intervall: {args.interval} Min. – Strg+C zum Stoppen")

    try:
        while True:
            messwert = await lade_messwert(args.id, args.timeout, args.debug)
            if messwert:
                zeit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(csv_datei, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([zeit, args.id, messwert])
                if args.debug:
                    print(f"{zeit} → ✅ {messwert} µSv/h → gespeichert in {csv_datei}")
            else:
                zeit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if args.debug:
                    print(f"{zeit} → ⚠️ Kein Messwert gespeichert")

            await asyncio.sleep(args.interval * 60)

    except KeyboardInterrupt:
        print("\n📥 Messung gestoppt.")

if __name__ == "__main__":
    asyncio.run(main())
