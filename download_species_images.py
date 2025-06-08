import os
import json
import requests

# 🔐 Hardcoded Unsplash API Key — REPLACE THIS with your actual key
UNSPLASH_KEY = "6tJFR4XgJctp3HRPEmokXjfcNHZk6n3LlaCjdnSu7_4"

ASSETS_DIR = "assets"
SEARCH_URL = "https://api.unsplash.com/search/photos"

if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

with open("species.json", "r") as f:
    species_data = json.load(f)["species"]

headers = {
    "Accept-Version": "v1",
    "Authorization": f"Client-ID {UNSPLASH_KEY}"
}

for fish in species_data:
    name = fish["common_name"]
    filename = os.path.join(ASSETS_DIR, f"{name.lower().replace(' ', '_')}.jpg")

    if os.path.exists(filename):
        print(f"✅ Already exists: {filename}")
        continue

    print(f"🔍 Searching image for: {name}")
    params = {"query": f"{name} fish", "per_page": 1}

    try:
        response = requests.get(SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        results = response.json()["results"]

        if not results:
            print(f"❌ No image found for: {name}")
            continue

        image_url = results[0]["urls"]["small"]
        image = requests.get(image_url).content

        with open(filename, "wb") as f:
            f.write(image)

        print(f"✅ Downloaded: {filename}")

    except Exception as e:
        print(f"❌ Failed for {name}: {e}")
