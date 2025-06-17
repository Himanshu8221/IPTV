import os
import requests
from dotenv import load_dotenv
from collections import defaultdict
from difflib import get_close_matches
import subprocess
import re

# Load .env variables
load_dotenv()
M3U_URL = os.getenv("M3U_URL")

# Define categories and channel names
CATEGORIES = {
    "Entertainment": [
        "Star Plus", "Star Plus HD", "Star Bharat", "Star Bharat HD", "Sony TV", "Sony TV HD", "Sony SAB", "Sony SAB HD", "Colors TV", "Colors TV HD",
        "Zee TV", "Zee TV HD',  "Zee Anmol", "Sony Pal", "& TV", "& TV HD"
    ],
    "Movies": [
        "Star Gold", "Star Gold HD", "Star Gold Select", "Star Gold Select HD", "Zee Cinema", "Zee Cinema HD", "Zee Action", "Zee Bollywood", "Zee Classic",
        "Sony Max", "Sony Max HD", "Sony Max 2", "Sony Wah", "Colors Cineplex", "Colors Cineplex HD", "Colors Cineplex Superhits", "& pictures", "& pictures HD",
        "UTV Movies", "UTV Action", "B4U Movies", "Zee Anmol Cinema"
    ],
    "Kids": [
        "Cartoon Network", "Pogo", "Hungama TV", "Disney Channel", "Nick", "Nick HD+", "Discovery Kids"
    ],
    "Knowledge": [
        "Discovery Channel", "Discovery Science", "National Geographic", "History TV18", "Animal Planet"
    ],
    "Sports": [
        "Star Sports", "Star Sports 1", "Star Sports 1 HD", "Star Sports 1 Hindi", "Star Sports 1 Hindi HD",
        "Star Sports 2", "Star Sports 2 HD", "Star Sports 3", "Star Sports First",
        "Sony Ten", "Sony Ten 1", "Sony Ten 1 HD", "Sony Ten 1 Hindi", "Sony Ten 2", "Sony Ten 2 HD",
        "Sony Ten 3", "Sony Ten 3 HD", "Sony Ten 3 Hindi", "Sony Ten 4", "Sony Six", "Sony Six HD",
        "Sports18", "Sports18 1", "Sports18 1 HD", "Sports18 2", "Sports18 2 HD", "Sports18 Hindi",
    ]
}

# Flatten all channel names for matching
CHANNEL_TO_CATEGORY = {
    name: category
    for category, names in CATEGORIES.items()
    for name in names
}

def fetch_m3u(url):
    print(f"📡 Fetching playlist from {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def fuzzy_match(channel_name):
    matches = get_close_matches(channel_name, CHANNEL_TO_CATEGORY.keys(), n=1, cutoff=0.85)
    return matches[0] if matches else None

def update_group_title(extinf_line, new_group):
    # Replace group-title="..." with new category
    if 'group-title="' in extinf_line:
        return re.sub(r'group-title=".*?"', f'group-title="{new_group}"', extinf_line)
    else:
        # If group-title is missing, add it
        return extinf_line.replace('#EXTINF:', f'#EXTINF:-1 group-title="{new_group}"', 1)

def categorize_and_rewrite(m3u_text):
    output = ["#EXTM3U\n"]
    lines = m3u_text.splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith("#EXTINF"):
            extinf = lines[i].strip()
            url = lines[i + 1].strip()
            channel_name = extinf.split(",")[-1].strip()
            matched_name = fuzzy_match(channel_name)
            if matched_name:
                category = CHANNEL_TO_CATEGORY[matched_name]
                extinf = update_group_title(extinf, category)
                output.append(extinf)
                output.append(url)
        i += 1
    return "\n".join(output)

def save_output(content, path="extracted_channels.m3u"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content + "\n")
    print(f"✅ Saved categorized playlist to {path}")

def auto_git_push(filepath):
    try:
        subprocess.run(["git", "add", filepath], check=True)
        subprocess.run(["git", "commit", "-m", "Updated playlist with categorized group-titles"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Changes pushed to GitHub.")
    except subprocess.CalledProcessError:
        print("❌ Git push failed. Please check your setup.")

def main():
    if not M3U_URL:
        print("❌ M3U_URL not found in .env")
        return
    try:
        m3u_text = fetch_m3u(M3U_URL)
        categorized = categorize_and_rewrite(m3u_text)
        save_output(categorized)
        auto_git_push("extracted_channels.m3u")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
