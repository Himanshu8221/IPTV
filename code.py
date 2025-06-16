import requests
import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load M3U URL from .env
load_dotenv()
M3U_URL = os.getenv("M3U_URL")
if not M3U_URL:
    print("❌ Error: M3U_URL not set in .env file.")
    sys.exit(1)

# ✅ Output file
OUTPUT_FILE = "list.m3u"

# ✅ Tata Play tvg-id map
tvg_id_map = {
    "Star Plus HD": "ts115", "Star Plus": "ts117",
    "Star Bharat HD": "ts121", "Star Bharat": "ts122",
    "Sony SAB HD": "ts132", "Sony SAB": "ts134",
    "&TV HD": "ts137", "&TV": "ts139",
    "Zee TV HD": "ts141", "Zee TV": "ts143",
    "Colors HD": "ts147", "Colors": "ts149",
    "Star Gold HD": "ts308", "Star Gold": "ts310",
    "Sony Max HD": "ts312", "Sony Max": "ts314",
    "Zee Cinema HD": "ts319", "Zee Cinema": "ts321",
    "Cartoon Network": "ts657", "Nickelodeon": "ts659", "Nick Jr": "ts661",
    "Disney Channel": "ts663", "Disney Junior": "ts665", "Pogo": "ts667",
    "Hungama": "ts669", "Discovery Channel": "ts401", "Discovery Science": "ts405",
    "Discovery Turbo": "ts407", "National Geographic": "ts411", "Nat Geo Wild": "ts413",
    "Animal Planet": "ts415", "History TV18": "ts417", "Sony BBC Earth": "ts419",
    "Epic": "ts421"
}

# ✅ Categories with match patterns
categories = {
    "Entertainment": ["Star Plus", "Star Bharat", "Sony TV", "Sony SAB", "Colors", "Zee TV", "&TV", "Big Magic", "Sony Pal", "Rishtey", "Star Utsav"],
    "Movies": ["Star Gold", "Sony Max", "Zee Cinema", "&pictures", "UTV", "B4U", "Wah", "Filmy"],
    "Kids": ["Cartoon Network", "Nick", "Nick Jr", "Sonic", "Pogo", "Baby TV", "Disney", "Hungama", "Marvel HQ"],
    "Knowledge": ["Discovery", "National Geographic", "Animal Planet", "BBC Earth", "History TV18", "Epic", "Fox Life"]
}

# ✅ Helper to match tvg-id
def find_tvg_id(name):
    for key, val in tvg_id_map.items():
        if key.lower() in name.lower():
            return val
    return ""

# ✅ Fetch M3U from URL
def fetch_m3u(url):
    try:
        print("📡 Fetching M3U...")
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"❌ Failed to fetch M3U: {e}")
        sys.exit(1)

# ✅ Filter and categorize
def filter_and_patch_m3u(content):
    lines = content.splitlines()
    result = ["#EXTM3U"]
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            line = lines[i]
            url = lines[i+1] if i+1 < len(lines) else ""
            name_match = re.search(r",(.*)", line)
            name = name_match.group(1).strip() if name_match else ""

            # Category
            group = None
            for cat, keywords in categories.items():
                if any(k.lower() in name.lower() for k in keywords):
                    group = cat
                    break

            if group:
                # Insert group-title and tvg-id
                line = re.sub(r'group-title="[^"]*"', '', line)
                line = re.sub(r'#EXTINF:', f'#EXTINF: group-title="{group}"', line, 1)

                tvg_match = re.search(r'tvg-id="(.*?)"', line)
                if tvg_match and tvg_match.group(1) == "":
                    tvg_id = find_tvg_id(name)
                    if tvg_id:
                        line = line.replace('tvg-id=""', f'tvg-id="{tvg_id}"')
                elif 'tvg-id' not in line:
                    tvg_id = find_tvg_id(name)
                    if tvg_id:
                        line = line.replace('#EXTINF:', f'#EXTINF: tvg-id="{tvg_id}"', 1)

                result.extend([line.strip(), url.strip()])
            i += 2
        else:
            i += 1
    return "\n".join(result)

# ✅ Save result
def save_file(text, path):
    Path(path).write_text(text, encoding='utf-8')
    print(f"✅ Saved to {path}")

# ✅ Main flow
def main():
    raw = fetch_m3u(M3U_URL)
    patched = filter_and_patch_m3u(raw)
    save_file(patched, OUTPUT_FILE)

if __name__ == "__main__":
    main()
