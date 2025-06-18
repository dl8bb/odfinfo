import argparse
import asyncio
import csv
from datetime import datetime
import requests

def fetch_latest_measurement(station_id, timeout=30, debug=False):
    url = (
        "https://www.imis.bfs.de/ogc/opendata/ows"
        "?service=WFS"
        "&version=1.1.0"
        "&request=GetFeature"
        "&typeName=opendata:odlinfo_timeseries_odl_1h"
        "&outputFormat=application/json"
        f"&viewparams=kenn:{station_id}"
        "&sortBy=end_measure+D"
        "&maxFeatures=1"
    )

    if debug:
        print(f"🌐 Request: {url}")

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        feature = data["features"][0]["properties"]

        return {
            "name": feature["name"],
            "value": feature["value"],
            "unit": feature["unit"],
            "timestamp": feature["end_measure"],
        }

    except (requests.RequestException, KeyError, IndexError) as e:
        if debug:
            print(f"❌ Fehler beim Abruf: {e}")
        return None

async def main():
    parser = argparse.ArgumentParser(description="ODL-Messwertabruf via JSON-API (BfS)")
    parser.add_argument("--id", required=True, help="Messstellen-ID (z.B. 031520061)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in Sekunden (Default: 30)")
    parser.add_argument("--interval", type=int, default=5, help="Intervall in Minuten (Default: 5)")
    parser.add_argument("--debug", action="store_true", help="Debug-Ausgaben aktivieren")
    parser.add_argument("--once", action="store_true", help="Nur einmaliger Abruf")

    args = parser.parse_args()
    csv_file = f"odlinfo_json_{args.id}_{datetime.now().strftime('%Y-%m-%d')}.csv"

    def log_to_csv(measurement):
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                args.id,
                measurement["name"],
                measurement["value"],
                measurement["unit"],
                measurement["timestamp"]
            ])

    if args.once:
        result = fetch_latest_measurement(args.id, args.timeout, args.debug)
        if result:
            print(f"{result['name']} {result['value']} {result['unit']} (letzte Messung: {result['timestamp']})")
            log_to_csv(result)
        else:
            print("⚠️ Kein Messwert verfügbar")
    else:
        print(f"⏱️ Starte Messung für ID {args.id} – alle {args.interval} Minuten")
        try:
            while True:
                result = fetch_latest_measurement(args.id, args.timeout, args.debug)
                if result:
                    print(f"{result['name']} {result['value']} {result['unit']} (letzte Messung: {result['timestamp']})")
                    log_to_csv(result)
                else:
                    print("⚠️ Kein Messwert verfügbar")
                await asyncio.sleep(args.interval * 60)
        except KeyboardInterrupt:
            print("\n📥 Messung gestoppt.")

if __name__ == "__main__":
    asyncio.run(main())
