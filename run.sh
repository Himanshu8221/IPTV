#!/data/data/com.termux/files/usr/bin/bash

echo "📦 Setting up Python environment..."

# Optional: create virtual environment (you can remove if not needed)
if [ ! -d "venv" ]; then
  python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "🚀 Running IPTV channel fetch + filter script..."
echo "📡 Fetching M3U content..."

# Run your Python script here
python3 code.py  # ✅ FIXED this line

echo "🔍 Filtering and categorizing channels..."
OUTPUT="list.m3u"

if [ -f "$OUTPUT" ]; then
  echo "✅ Filtered and categorized $(grep -c '^#EXTINF' "$OUTPUT") channels."
else
  echo "❌ Error: $OUTPUT not found!"
  exit 1
fi

echo "📦 Committing and pushing to GitHub..."
echo "venv/" > .gitignore
git add .gitignore
git add "$OUTPUT"

if ! git diff --cached --quiet; then
  git commit -m "Update filtered M3U playlist"
  git push
else
  echo "✅ No changes to commit."
fi

deactivate
