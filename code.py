import os
import requests
import subprocess
from dotenv import load_dotenv
from collections import defaultdict
from difflib import get_close_matches

# Load M3U URL from .env
load_dotenv()
M3U_URL = os.getenv("M3U_URL")

# Define your categories with exact or near channel names
CATEGORIES = {
    "Entertainment": [
        "Star Plus", "Star Plus HD", "Star Bharat", "Sony TV", "Sony SAB", "Colors TV",
        "Zee TV", "Zee Anmol", "Sony Pal", "& TV"
    ],
    "Movies": [
        "Star Gold", "Star Gold Select", "Zee Cinema", "Zee Action", "Zee Bollywood", "Zee Classic",
        "Sony Max", "Sony Max 2", "Sony Wah", "Colors Cineplex", "& pictures", "UTV Movies",
        "UTV Action", "B4U Movies", "Zee Anmol Cinema"
    ],
    "Kids": [
        "Cartoon Network", "Pogo", "Hungama TV", "Disney Channel", "Nick", "Nick HD+", "Discovery Kids"
    ],
    "Knowledge": [
        "Discovery Channel", "Discovery Science", "National Geographic", "History TV18", "Animal Planet"
    ],
    "Sports": [
        "Star Sports", "Sony Ten", "Sony Six", "Sony Ten 1", "Sony Ten 2", "Sony Ten 3", "Sony Ten 4", "Sports18"
    ]
}

# Invert category -> channels to name -> category mapping
CHANNEL_TO_CATEGORY = {
    channel: category
    for category, channels in CATEGORIES.items()
    for channel in channels
}

def fetch_m3u(url):
    print(f"📡 Fetching M3U from {url}")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Failed to fetch: {r.status_code}")
    return r.text

def fuzzy_match(name):
    candidates = get_close_matches(name, CHANNEL_TO_CATEGORY.keys(), n=1, cutoff=0.85)
    return candidates[0] if candidates else None

def parse_and_group(m3u_text):
    grouped = defaultdict(list)
    lines = m3u_text.splitlines()
    i = 0

    while i < len(lines) - 1:
        if lines[i].startswith("#EXTINF"):
            extinf = lines[i]
            url = lines[i + 1]
            try:
                channel_name = extinf.split(",")[-1].strip()
                match = fuzzy_match(channel_name)
                if match:
                    category = CHANNEL_TO_CATEGORY[match]
                    grouped[category].append(f"{extinf}\n{url}")
            except Exception as e:
                print(f"Error parsing line {i}: {e}")
            i += 2
        else:
            i += 1
    return grouped

def write_output(grouped, output_file="extracted_channels.m3u"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for category in CATEGORIES.keys():
            if category in grouped:
                f.write(f"# --- {category} ---\n")
                for item in grouped[category]:
                    f.write(item + "\n")
    print(f"💾 Saved to {output_file}")

def auto_push(filename):
    try:
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(["git", "commit", "-m", "Auto update extracted channels grouped by name"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Auto-pushed to GitHub.")
    except subprocess.CalledProcessError:
        print("❌ Git push failed. Make sure Git is set up correctly.")

def main():
    if not M3U_URL:
        print("❌ M3U_URL not set in .env")
        return

    try:
        m3u_data = fetch_m3u(M3U_URL)
        grouped = parse_and_group(m3u_data)
        write_output(grouped)
        auto_push("extracted_channels.m3u")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
