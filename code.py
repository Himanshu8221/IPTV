import os
import requests
import subprocess
from dotenv import load_dotenv
from collections import defaultdict

# Load M3U_URL from .env file
load_dotenv()
M3U_URL = os.getenv("M3U_URL")

# Categories for sorting channels
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

def fetch_m3u(url):
    print(f"📡 Fetching M3U from {url}...")
    response = requests.get(url)
    if response.ok:
        print("✅ M3U fetched successfully.")
        return response.text
    else:
        raise Exception(f"❌ Failed to fetch M3U: {response.status_code}")

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

def save_m3u(categorized, output_path="list.m3u"):
    with open(output_path, "w", encoding="utf-8") as f:
        for category, entries in categorized.items():
            f.write(f"# --- {category} Channels ---\n")
            for entry in entries:
                f.write(entry + "\n")
    print(f"📁 Saved categorized channels to {output_path}")

def auto_git_push(filepath):
    try:
        subprocess.run(["git", "add", filepath], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-update list.m3u"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Changes pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")

def main():
    if not M3U_URL:
        print("❌ M3U_URL not set in .env file.")
        return
    try:
        m3u_data = fetch_m3u(M3U_URL)
        categorized = categorize_channels(m3u_data)
        output_file = "list.m3u"
        save_m3u(categorized, output_file)
        auto_git_push(output_file)
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
