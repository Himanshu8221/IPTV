import os
import requests
from dotenv import load_dotenv
from collections import defaultdict
from difflib import get_close_matches
import subprocess

# Load environment variables
load_dotenv()
M3U_URL = os.getenv("M3U_URL")

# Define channel categories by name
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

# Flatten for fuzzy matching
ALL_KNOWN_CHANNELS = {
    name: category
    for category, names in CATEGORIES.items()
    for name in names
}

def fetch_m3u(url):
    print(f"📡 Fetching playlist from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    raise Exception(f"Failed to fetch M3U file. Status code: {response.status_code}")

def fuzzy_match(name):
    matches = get_close_matches(name, ALL_KNOWN_CHANNELS.keys(), n=1, cutoff=0.85)
    return matches[0] if matches else None

def categorize_channels(m3u_text):
    categorized = defaultdict(list)
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
                    category = ALL_KNOWN_CHANNELS[match]
                    categorized[category].append(f"{extinf}\n{url}")
            except Exception as e:
                print(f"Error processing line {i}: {e}")
            i += 2
        else:
            i += 1
    return categorized

def save_output(categorized, path="extracted_channels.m3u"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for category in CATEGORIES.keys():
            if category in categorized:
                f.write(f"# --- {category} ---\n")
                for item in categorized[category]:
                    f.write(item + "\n")
                f.write("\n")
    print(f"✅ Channels categorized and saved to {path}")

def auto_git_push(filepath):
    try:
        subprocess.run(["git", "add", filepath], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-update extracted channels by name"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Auto-pushed to GitHub.")
    except subprocess.CalledProcessError:
        print("❌ Git push failed. Check your Git config.")

def main():
    if not M3U_URL:
        print("❌ M3U_URL not set in .env")
        return
    try:
        m3u_text = fetch_m3u(M3U_URL)
        categorized = categorize_channels(m3u_text)
        save_output(categorized)
        auto_git_push("extracted_channels.m3u")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
