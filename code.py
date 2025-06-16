import requests
import os
import subprocess
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List

# ✅ Load environment
load_dotenv()
M3U_URL = os.getenv("M3U_URL")
if not M3U_URL:
    print("❌ Error: M3U_URL not set in .env.")
    sys.exit(1)

OUTPUT_FILE = "list.m3u"
COMMIT_MESSAGE = "Update filtered M3U playlist"

# ✅ Categories (keep yours)
def compile_channels(channels: List[str]) -> List[re.Pattern]:
    return [re.compile(c, re.IGNORECASE) for c in channels]

categories: Dict[str, List[re.Pattern]] = {
    "Entertainment": compile_channels(["Star Plus", "Star Bharat", "Sony TV", "Sony SAB", "Colors TV", "Zee TV", "Zee Anmol", "Sony Pal", "Star Utsav", "Big Magic"]),
    "Movies": compile_channels(["Star Gold", "Zee Cinema", "Zee Action", "Sony Max", "Sony Wah", "Colors Cineplex", "&pictures", "UTV", "B4U", "Filmy"]),
    "Kids": compile_channels(["Nick", "Cartoon Network", "Pogo", "Hungama", "Disney", "Marvel HQ", "Baby TV", "Discovery Kids"]),
    "Knowledge": compile_channels(["Discovery", "BBC Earth", "History", "National Geographic", "Animal Planet", "Epic", "Fox Life"])
}

# ✅ Fetch playlist
def fetch_m3u(url: str) -> str:
    try:
        print(f"📡 Fetching M3U from {url}")
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"❌ Failed to fetch: {e}")
        sys.exit(1)

# ✅ Filter + format
def filter_m3u(content: str) -> str:
    print("🔍 Filtering and formatting...")
    lines = content.splitlines()
    result = ["#EXTM3U"]
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            info = lines[i]
            url = lines[i+1] if i+1 < len(lines) else ""

            # Extract channel name
            name_match = re.search(r",(.*)", info)
            channel_name = name_match.group(1).strip() if name_match else ""
            found = False

            for group, patterns in categories.items():
                if any(p.search(channel_name) for p in patterns):
                    # Clean old group-title
                    info = re.sub(r'group-title="[^"]*"', '', info)
                    # Ensure -1 format
                    info = re.sub(r'#EXTINF[^:]*:', '#EXTINF:-1', info)
                    # Add group-title
                    if 'group-title=' not in info:
                        info = info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{group}"')
                    # Clean spacing
                    info = re.sub(r",(?! )", ", ", info)

                    result.append(info.strip())
                    result.append(url.strip())
                    found = True
                    break

            i += 2 if found else 1
        else:
            i += 1
    print(f"✅ {len(result)//2} categorized channels.")
    return "\n".join(result)

# ✅ Save output
def save_file(content: str, path: Path):
    path.write_text(content, encoding="utf-8")
    print(f"💾 Saved: {path}")

# ✅ Push to Git
def git_push(repo_path: Path, filename: str, message: str):
    print("📦 Preparing Git commit...")
    subprocess.run(["git", "-C", str(repo_path), "add", filename], check=True)

    # Show diff for debug
    subprocess.run(["git", "-C", str(repo_path), "diff", "--cached"])

    # Only commit if changes exist
    result = subprocess.run(["git", "-C", str(repo_path), "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "-C", str(repo_path), "commit", "-m", message], check=True)
        subprocess.run(["git", "-C", str(repo_path), "push"], check=True)
        print("🚀 Pushed to GitHub.")
    else:
        print("✅ No Git changes to commit.")

# ✅ Main
def main():
    raw = fetch_m3u(M3U_URL)
    processed = filter_m3u(raw)
    output_path = Path(OUTPUT_FILE)
    save_file(processed, output_path)
    git_push(Path.cwd(), OUTPUT_FILE, COMMIT_MESSAGE)

if __name__ == "__main__":
    main()
