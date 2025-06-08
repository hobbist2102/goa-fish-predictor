import os
import json
import requests
from pathlib import Path
from urllib.parse import quote

# Make sure assets folder exists
Path("assets").mkdir(parents=True, exist_ok=True)

# Load species list
with open("species.json", "r") as f:
    species_list = json.load(f)["species"]

# DuckDuckGo Image Search API (Unofficial, fast)
def fetch_duckduckgo_image(query):
    url = f"https://duckduckgo.com/i.js?q={quote(query)}&o=json"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0]["image"]
    except Exception as e:
        print(f"Error fetching image for {query}: {e}")
    return None

# Main loop
for sp in species_list:
    name = sp["common_name"]
    safe_name = name.lower().replace(" ", "_")
    filepath = f"assets/{safe_name}.jpg"

    if os.path.exists(filepath):
        print(f"✔️ {safe_name}.jpg already exists.")
        continue

    print(f"🔍 Searching image for: {name}")
    img_url = fetch_duckduckgo_image(name + " fish")
    if img_url:
        try:
            img_data = requests.get(img_url).content
            with open(filepath, "wb") as f:
                f.write(img_data)
            print(f"✅ Downloaded: {filepath}")
        except Exception as e:
            print(f"❌ Failed to save {name}: {e}")
    else:
        print(f"❌ No image found for: {name}")
