import requests
import os
import subprocess
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ M3U playlist URL
M3U_URL = os.getenv("M3U_URL", "http://starshare.org:80/get.php?username=gurmeet&password=gurmeet&type=m3u_plus&output=mpegts")
OUTPUT_FILE = "list.m3u"
HTML_FILE = "preview.html"
COMMIT_MESSAGE = "Update Hindi-only filtered M3U and preview"

# ✅ Hindi channels only
entertainment_channels = ["Star Plus", "Star Bharat", "Sony TV", "Sony SAB", "Colors TV", "Zee TV", "Zee Anmol", "Sony Pal"]
movie_channels = ["Star Gold", "Star Gold 2", "Zee Cinema", "Zee Action", "Sony Max", "Sony Max 2", "Sony Wah", "Colors Cineplex", "Zee Anmol Cinema", "&pictures"]
kids_channels = ["Hungama TV", "Disney Channel", "Nick", "Sonic"]
knowledge_channels = ["Discovery Channel", "Discovery Science", "National Geographic", "History TV18"]
sports_channels = ["Star Sports 1 Hindi", "Sony Ten 3", "Sports18"]

# ✅ Categorize
categories = {
    "Entertainment": entertainment_channels,
    "Movies": movie_channels,
    "Kids": kids_channels,
    "Knowledge": knowledge_channels,
    "Sports": sports_channels
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
    print("🔍 Filtering and categorizing Hindi channels...")
    lines = content.splitlines()
    filtered = []

    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf = lines[i]
            url = lines[i + 1] if i + 1 < len(lines) else ""
            matched = False

            for category, channel_list in categories.items():
                for channel in channel_list:
                    if re.search(rf'\b{channel}\b', extinf, re.IGNORECASE):
                        extinf = re.sub(r'group-title="[^"]+"', '', extinf)
                        extinf = re.sub(r'#EXTINF:[^,]*,', f'#EXTINF:-1 group-title="{category}",', extinf)
                        filtered.append(extinf)
                        filtered.append(url)
                        matched = True
                        break
                if matched:
                    break
        i += 1

    print(f"✅ Found {len(filtered) // 2} Hindi channels.")
    return "#EXTM3U\n" + "\n".join(filtered)

def save_file(content, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Saved filtered M3U to {path}")

def generate_html_preview(m3u_path, html_output="preview.html"):
    print("🌐 Generating HTML preview...")
    with open(m3u_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    html = ['<html><head><meta charset="UTF-8"><title>Hindi IPTV Preview</title></head><body>']
    html.append('<h2>📺 Hindi IPTV Channel List</h2><ul>')

    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            channel_name = re.sub(r'.*?,', '', lines[i]).strip()
            stream_url = lines[i + 1].strip() if i + 1 < len(lines) else "#"
            html.append(f'<li><strong>{channel_name}</strong> - <a href="{stream_url}" target="_blank">Play</a></li>')

    html.append('</ul></body></html>')

    with open(html_output, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    print(f"✅ HTML preview saved to: {html_output}")

def git_push(repo_path, filename, message):
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print("❌ Not a Git repository.")
        return

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
    output_path = Path.cwd() / OUTPUT_FILE
    html_path = Path.cwd() / HTML_FILE

    save_file(filtered, output_path)
    generate_html_preview(output_path, html_path)
    git_push(str(Path.cwd()), OUTPUT_FILE, COMMIT_MESSAGE)
    git_push(str(Path.cwd()), HTML_FILE, "Update HTML preview")

if __name__ == "__main__":
    main()
