
import requests
import os
import subprocess
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
M3U_URL = os.getenv("M3U_URL")
OUTPUT_FILE = "list.m3u"
COMMIT_MESSAGE = "Update filtered M3U playlist"

# ✅ Define exact channel match per category
categories = {
    "Entertainment": [
        "Star Plus", "Star Bharat", "Sony TV", "Sony SAB", "Colors TV", "Zee TV", "Zee Anmol", "Sony Pal", "& TV"
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
    try:
        print("📡 Fetching M3U content...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Failed to fetch M3U: {e}")
        sys.exit(1)

def filter_m3u(content):
    print("🔍 Filtering for only allowed channels...")
    lines = content.splitlines()
    filtered = []

    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            line = lines[i]
            url = lines[i + 1] if i + 1 < len(lines) else ""

            name_match = re.search(r'tvg-name="([^"]+)"', line)
            channel_name = name_match.group(1).strip() if name_match else ""

            for category, channel_list in categories.items():
                if any(ch.lower() in channel_name.lower() for ch in channel_list):
                    # Update group-title
                    if 'group-title="' in line:
                        line = re.sub(r'group-title="[^"]+"', f'group-title="{category}"', line)
                    else:
                        line = line.replace("#EXTINF:", f'#EXTINF: group-title="{category}",')
                    filtered.append(line)
                    filtered.append(url)
                    break  # Only first matched category is used

    print(f"✅ Kept {len(filtered)//2} matched channels.")
    return "#EXTM3U\n" + "\n".join(filtered)

def save_file(content, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Saved filtered list to {path}")

def git_push(repo_path, filename, message):
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print("❌ Not a Git repository. Please initialize with `git init`.")
        sys.exit(1)

    try:
        os.chdir(repo_path)
        subprocess.run(["git", "config", "user.name", "Himanshu8221"], check=True)
        subprocess.run(["git", "config", "user.email", "Himanshusingh8527186817@gmail.com"], check=True)

        subprocess.run(["git", "pull"], check=True)
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push"], check=True)

        print("🚀 Pushed to GitHub successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        sys.exit(1)

def main():
    m3u_content = fetch_m3u(M3U_URL)
    filtered = filter_m3u(m3u_content)

    repo_path = Path.cwd()
    output_path = repo_path / OUTPUT_FILE

    save_file(filtered, output_path)
    git_push(str(repo_path), OUTPUT_FILE, COMMIT_MESSAGE)

if __name__ == "__main__":
    main()
