import os
import requests
from dotenv import load_dotenv
from collections import defaultdict

# Load .env file
load_dotenv()
M3U_URL = os.getenv("M3U_URL")

# Predefined categories
CATEGORIES = {
    "Entertainment": [
        "Star Plus", "Star Plus HD", "Star Bharat", "Sony TV", "Sony SAB", "Colors TV", "Zee TV", "Zee Anmol", "Sony Pal", "& TV"
    ],
    "Movies": [
        "Star Gold", "Star Gold Select", "Zee Cinema", "Zee Action", "Zee Bollywood", "Zee Classic",
        "Sony Max", "Sony Max 2", "Sony Wah", "Colors Cineplex", "& pictures", "UTV Movies", "UTV Action", "B4U Movies", "Zee Anmol Cinema"
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

# Download M3U content
def fetch_m3u(url):
    print(f"Fetching M3U from {url}...")
    response = requests.get(url)
    if response.ok:
        return response.text
    else:
        raise Exception(f"Failed to fetch M3U: {response.status_code}")

# Categorize channels
def categorize_channels(m3u_content):
    categorized = defaultdict(list)
    lines = m3u_content.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF:"):
            channel_line = lines[i]
            url_line = lines[i + 1] if i + 1 < len(lines) else ""
            for category, names in CATEGORIES.items():
                for name in names:
                    if name.lower() in channel_line.lower():
                        categorized[category].append(f"{channel_line}\n{url_line}")
                        break
            i += 2
        else:
            i += 1
    return categorized

# Save categorized channels
def save_m3u(categorized, output_path="list.m3u"):
    with open(output_path, "w", encoding="utf-8") as f:
        for category, entries in categorized.items():
            f.write(f"# --- {category} Channels ---\n")
            for entry in entries:
                f.write(entry + "\n")
    print(f"✅ Extracted channels saved to {output_path}")

def main():
    if not M3U_URL:
        print("❌ M3U_URL is not set in the .env file.")
        return
    try:
        m3u_data = fetch_m3u(M3U_URL)
        categorized = categorize_channels(m3u_data)
        save_m3u(categorized)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
