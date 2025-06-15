import requests
import os
import subprocess
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List

# ✅ Load .env file
load_dotenv()

# ✅ Read M3U URL from .env
M3U_URL = os.getenv("M3U_URL")
if not M3U_URL:
    print("❌ Error: M3U_URL not set in .env file.")
    sys.exit(1)

# ✅ Output file and commit message
OUTPUT_FILE = "list.m3u"
COMMIT_MESSAGE = "Update filtered M3U playlist"

# ✅ Define categories with precompiled patterns
def compile_channels(channels: List[str]) -> List[re.Pattern]:
    return [re.compile(c, re.IGNORECASE) for c in channels]

categories: Dict[str, List[re.Pattern]] = {
    "Entertainment": compile_channels([
        "Star Plus", "Star Plus HD", "Star Plus FHD", "Star Plus\\(FHD\\)", "Star Plus 4K",
        "Star Bharat", "Star Bharat HD", "Star Bharat FHD", "Star Bharat\\(FHD\\)", "Star Bharat 4K",
        "Sony TV", "Sony TV HD", "Sony TV FHD", "Sony TV\\(FHD\\)", "Sony TV 4K",
        "Sony SAB", "Sony SAB HD", "Sony SAB FHD", "Sony SAB\\(FHD\\)", "Sony SAB 4K",
        "Colors TV", "Colors TV HD", "Colors TV FHD", "Colors TV\\(FHD\\)", "Colors TV 4K",
        "Zee TV", "Zee TV HD", "Zee TV FHD", "Zee TV\\(FHD\\)", "Zee TV 4K",
        "Zee Anmol", "Zee Anmol Cinema", "Colors Rishtey", "Sony Pal", "Star Utsav", "Big Magic", "DD National", "Zee Hindustan"
    ]),
    "Movies": compile_channels([
        "Star Gold", "Star Gold HD", "Star Gold FHD", "Star Gold 4K", "Star Gold Select", "Star Gold 2",
        "Zee Cinema", "Zee Cinema HD", "Zee Action", "Zee Bollywood", "Zee Classic",
        "Sony Max", "Sony Max HD", "Sony Max FHD", "Sony Max 2", "Sony Wah",
        "Colors Cineplex", "Colors Cineplex HD", "Colors Cineplex FHD", "Colors Cineplex 4K",
        "&pictures", "&pictures HD", "&xplor HD",
        "UTV Movies", "UTV Action", "B4U Movies", "Filmy"
    ]),
    "Kids": compile_channels([
        "Cartoon Network", "Pogo", "Hungama TV", "Disney Channel", "Disney Junior", "Disney XD",
        "Nick", "Nick HD\\+", "Sonic", "Marvel HQ", "Baby TV", "Discovery Kids"
    ]),
    "Knowledge": compile_channels([
        "Sony BBC Earth", "Sony BBC Earth HD", "Discovery Channel", "Discovery HD", "Discovery Science", "Discovery Turbo",
        "National Geographic", "National Geographic HD", "History TV18", "Animal Planet", "Animal Planet HD",
        "Fox Life", "Epic", "DD Kisan", "DD India"
    ])
}

# ✅ Fetch the M3U content from URL
def fetch_m3u(url: str) -> str:
    try:
        print("📡 Fetching M3U content...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"❌ M3U fetch failed: {e}")
        sys.exit(1)

# ✅ Filter and categorize M3U channels
def filter_m3u(content: str) -> str:
    print("🔍 Filtering and categorizing channels...")
    lines = content.splitlines()
    filtered = []
    total = len(lines)
    i = 0
    while i < total:
        line = lines[i]
        if line.startswith("#EXTINF"):
            url = lines[i + 1] if i + 1 < total else ""
            matched = False
            for category, patterns in categories.items():
                if any(pattern.search(line) for pattern in patterns):
                    line = re.sub(r'group-title="[^"]+"', '', line)
                    line = re.sub(r'#EXTINF:', f'#EXTINF: group-title="{category}",', line, 1)
                    filtered.extend([line.strip(), url.strip()])
                    matched = True
                    break
            i += 2 if matched else 1
        else:
            i += 1
    print(f"✅ Filtered and categorized {len(filtered)//2} channels.")
    return "#EXTM3U\n" + "\n".join(filtered)

# ✅ Save filtered output to file
def save_file(content: str, path: Path):
    path.write_text(content, encoding='utf-8')
    print(f"💾 Saved to {path}")

# ✅ Git automation: add, commit, push
def git_push(repo_path: Path, filename: str, message: str):
    if not (repo_path / ".git").is_dir():
        print("❌ Not a Git repo. Run `git init` first.")
        sys.exit(1)
    try:
        print("📦 Committing and pushing to GitHub...")
        subprocess.run(["git", "-C", str(repo_path), "config", "user.name", "Himanshu8221"], check=True)
        subprocess.run(["git", "-C", str(repo_path), "config", "user.email", "Himanshusingh8527186817@gmail.com"], check=True)
        subprocess.run(["git", "-C", str(repo_path), "pull"], check=True)
        subprocess.run(["git", "-C", str(repo_path), "add", filename], check=True)

        # ✅ Only commit if changes are staged
        result = subprocess.run(["git", "-C", str(repo_path), "diff", "--cached", "--quiet"])
        if result.returncode != 0:
            subprocess.run(["git", "-C", str(repo_path), "commit", "-m", message], check=True)
            subprocess.run(["git", "-C", str(repo_path), "push"], check=True)
            print("🚀 Pushed to GitHub successfully.")
        else:
            print("✅ No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")
        sys.exit(1)

# ✅ Main function
def main():
    m3u_data = fetch_m3u(M3U_URL)
    filtered_content = filter_m3u(m3u_data)
    repo_dir = Path.cwd()
    output_path = repo_dir / OUTPUT_FILE
    save_file(filtered_content, output_path)
    git_push(repo_dir, OUTPUT_FILE, COMMIT_MESSAGE)

if __name__ == "__main__":
    main()
