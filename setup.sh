#!/bin/bash

# setup.sh – Installationsskript für ODL-Info Scraper

set -e

echo "📦 Installiere notwendige Libraries..."
sudo apt update
sudo apt install libgtk-4-dev libgraphene-1.0-0 libatk-bridge2.0-0 libnss3 libxss1 libasound2

echo "📄 Erzeuge die Datei mit den Python-Abhängigkeiten..."
echo "playwright>=1.44" > requirements.txt
echo "requests" >> requirements.txt

echo "📦 Erstelle Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo "📄 Installiere Python-Abhängigkeiten..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🌐 Installiere Playwright-Browser..."
playwright install

echo "✅ Setup abgeschlossen. Aktiviere das venv mit:"
echo "source venv/bin/activate"
