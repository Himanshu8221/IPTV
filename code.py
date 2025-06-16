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
        "Star Plus", "Star Bharat", "Sony TV", "Sony SAB", "Colors TV", "Zee TV",
        "Zee Anmol", "Zee Anmol Cinema", "Colors Rishtey", "Sony Pal", "Star Utsav", "Big Magic", "DD National"
    ]),
    "Movies": compile_channels([
        "Star Gold", "Zee Cinema", "Zee Action", "Zee Bollywood", "Sony Max", "Sony Max 2",
        "Sony Wah", "Colors Cineplex", "&pictures", "&xplor", "UTV Movies", "UTV Action", "B4U Movies", "Filmy"
    ]),
    "Kids": compile_channels([
        "Cartoon Network", "Pogo", "Hungama", "Disney", "Nick", "Sonic", "Marvel HQ", "Baby TV", "Discovery Kids"
    ]),
    "Knowledge": compile_channels([
        "Sony BBC Earth", "Discovery", "Nat Geo", "History TV18", "Animal Planet", "Fox Life", "Epic", "DD Kisan", "DD India"
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
                    # Extract channel name
                    name_match = re.search(r',(.*)$', line)
                    channel_name = name_match.group(1).strip() if name_match else "Unknown"

                    # Preserve or fallback tvg-* fields
                    tvg_id = re.search(r'tvg-id="([^"]+)"', line)
                    tvg_name = re.search(r'tvg-name="([^"]+)"', line)
                    tvg_logo = re.search(r'tvg-logo="([^"]+)"', line)

                    # Rebuild EXTINF with all expected tags
                    new_line = f'#EXTINF:-1 group-title="{category}"'
                    new_line += f' tvg-id="{tvg_id.group(1)}"' if tvg_id else ''
                    new_line += f' tvg-name="{tvg_name.group(1) if tvg_name else channel_name}"'
                    new_line += f' tvg-logo="{tvg_logo.group(1)}"' if tvg_logo else ''
                    new_line += f',{channel_name}'

                    filtered.extend([new_line.strip(), url.strip()])
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
