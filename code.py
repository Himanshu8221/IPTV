import os
import requests
import subprocess
from dotenv import load_dotenv
from collections import defaultdict
from difflib import get_close_matches

# Load environment variables
load_dotenv()
M3U_URL = os.getenv("M3U_URL")

# Define your own custom categories and known channel names
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

# Flatten channel names for matching
ALL_KNOWN_CHANNELS = {name: cat for cat, names in CATEGORIES.items() for name in names}

def fetch_m3u(url):
    print(f"📡 Fetching M3U from {url}...")
    response = requests.get(url)
    if response.ok:
        print("✅ M3U fetched successfully.")
        return response.text
    else:
        raise Exception(f"❌ Failed to fetch M3U: {response.status_code}")

def fuzzy_match_channel_name(name):
    close = get_close_matches(name, ALL_KNOWN_CHANNELS.keys(), n=1, cutoff=0.8)
    return close[0] if close else None

def categorize_by_name(m3u_text):
    categorized = defaultdict(list)
    lines = m3u_text.splitlines()
    i = 0

    while i < len(lines) - 1:
        if lines[i].startswith("#EXTINF:"):
            info_line = lines[i]
            url_line = lines[i + 1]
            # Extract name after comma in EXTINF
            try:
                name = info_line.split(",")[-1].strip()
                matched = fuzzy_match_channel_name(name)
                if matched:
                    category = ALL_KNOWN_CHANNELS[matched]
                    categorized[category].append(f"{info_line}\n{url_line}")
            except Exception:
                pass
            i += 2
        else:
            i += 1

    return categorized

def save_output(categorized, path="extracted_channels.m3u"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for category, entries in categorized.items():
            f.write(f"# --- {category} ---\n")
            for entry in entries:
                f.write(entry + "\n")
    print(f"💾 Saved to {path}")

def auto_git_push(filepath):
    try:
        subprocess.run(["git", "add", filepath], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-update extracted channels by name"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")

def main():
    if not M3U_URL:
        print("❌ M3U_URL not set in .env")
        return

    try:
        m3u_data = fetch_m3u(M3U_URL)
        categorized = categorize_by_name(m3u_data)
        save_output(categorized)
        auto_git_push("extracted_channels.m3u")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
