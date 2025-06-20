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
        "Star Plus", "Star Plus HD", "Star Bharat", "Star Bharat HD", "Sony TV", "Sony TV HD", "Sony SAB", "Sony TV HD (1)", "Sony TV HD (2)",
        "Sony SAB HD", "Sony sab HD", "Colors TV", "Colors TV HD","IN | Zee TV", "Zee TV HD", "Zee Anmol", "Sony Pal", "IN | & TV", 
        "& TV HD", "IN | STAR PLUS", "STAR PLUS HD", "STAR BHARAT", "STAR BHARAT HD", "SONY TV", "SONY TV HD", "COLORS (FHD)", "Star Utsav",
        "IN | SONY SAB", "SONY SAB HD", "COLORS TV", "COLORS TV HD","ZEE TV", "ZEE TV HD", "ZEE ANMOL", "SONY PAL", "SONY HD", "COLOR HD", "COLORS FHD", "IN | SONY SET HD"
 ],
    "Movies": [
        "Star Gold", "Star Gold HD", "Star Gold Select", "Star Gold Select HD", "Zee Cinema", "Zee Cinema HD", "Zee Action", "Zee Bollywood", "Zee Classic",
        "Sony Max", "Sony Max HD", "Sony Max 2", "Sony Wah", "Colors Cineplex", "Colors Cineplex HD", "Colors Cineplex Superhits", "& pictures", "& pictures HD",
        "UTV Movies", "UTV Action", "B4U Movies", "Zee Anmol Cinema", "IN | STAR GOLD", "STAR GOLD HD", "STAR GOLD SELECT", "STAR GOLD SELECT HD", "ZEE CINEMA", 
        "ZEE CINEMA HD", "ZEE ACTION", "ZEE BOLLYWOOD", "ZEE CLASSIC", "SONY MAX", "SONY MAX HD", "SONY MAX 2", "SONY WAH", "COLORS CINEPLEX", 
        "COLORS CINEPLEX HD", "COLORS CINEPLEX SUPERHITS", "IN | & PICTURES", "& PICTURES HD","UTV MOVIES", "UTV ACTION", "B4U MOVIES", "ZEE ANMOL CINEMA"
],
    "Kids": [
        "Cartoon Network", "Pogo", "Hungama TV", "Disney Channel", "Nick", "Nick HD+", "Discovery Kids", "Nick Hindi", "Sony Yay"
    ],
    "Knowledge": [
        "Discovery Channel", "Discovery Science", "National Geographic", "History TV18", "Animal Planet"
    ],
    "Sports": [
        "Star Sports", "Star Sports 1", "Star Sports 1 HD", "Star Sports 1 Hindi", "Star Sports 1 Hindi HD",
        "Star Sports 2", "Star Sports 2 HD", "Star Sports 3", "Star Sports First",
        "Sony Ten", "Sony Ten 1", "Sony Ten 1 HD", "Sony Ten 1 Hindi", "Sony Ten 2", "Sony Ten 2 HD",
        "Sony Ten 3", "Sony Ten 3 HD", "Sony Ten 3 Hindi", "Sony Ten 4", "Sony Six", "Sony Six HD",
        "Sports18", "Sports18 1", "Sports18 1 HD", "Sports18 2", "Sports18 2 HD", "Sports18 Hindi", "STAR SPORTS", 
        "STAR SPORTS 1", "STAR SPORTS 1 HD", "STAR SPORTS 1 HINDI", "STAR SPORTS 1 HINDI HD",
        "STAR SPORTS 2", "STAR SPORTS 2 HD", "STAR SPORTS 3", "STAR SPORTS FIRST",
        "SONY TEN", "SONY TEN 1", "SONY TEN 1 HD", "SONY TEN 1 HINDI", "SONY TEN 2", "SONY TEN 2 HD",
        "SONY TEN 3", "SONY TEN 3 HD", "SONY TEN 3 HINDI", "SONY TEN 4", "SONY SIX", "SONY SIX HD",
        "SPORTS18", "SPORTS18 1", "SPORTS18 1 HD", "SPORTS18 2", "SPORTS18 2 HD", "SPORTS18 HINDI"
    ]
}

CHANNEL_TO_CATEGORY = {
    name: category
    for category, names in CATEGORIES.items()
    for name in names
}

def fetch_m3u(url):
    print(f"📡 Fetching playlist from {url}")
    headers = {
        "User-Agent": "VLC/3.0.11 LibVLC/3.0.11"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def fuzzy_match(channel_name):
    matches = get_close_matches(channel_name, CHANNEL_TO_CATEGORY.keys(), n=1, cutoff=0.85)
    return matches[0] if matches else None

def update_group_title(extinf_line, new_group):
    tvg_id = re.search(r'tvg-id="(.*?)"', extinf_line)
    tvg_name = re.search(r'tvg-name="(.*?)"', extinf_line)
    tvg_logo = re.search(r'tvg-logo="(.*?)"', extinf_line)
    channel_name = extinf_line.split(",")[-1].strip()

    new_extinf = '#EXTINF:-1'

    new_extinf += f' tvg-id="{tvg_id.group(1) if tvg_id else ""}"'
    new_extinf += f' tvg-name="{tvg_name.group(1) if tvg_name else channel_name}"'
    new_extinf += f' tvg-logo="{tvg_logo.group(1) if tvg_logo else ""}"'
    new_extinf += f' group-title="{new_group}",{channel_name}'

    return new_extinf

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

def save_output(content, path="list.m3u"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content + "\n")
    print(f"✅ Saved categorized playlist to {path}")

def auto_git_push(filepath):
    try:
        subprocess.run(["git", "add", filepath], check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode == 0:
            print("⚠️ No changes to commit.")
            return
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
        auto_git_push("list.m3u")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
