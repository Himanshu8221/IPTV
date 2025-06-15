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
python3 list.py

echo "🔍 Filtering and categorizing channels..."
# Assuming your script saves the output to list.m3u
OUTPUT="list.m3u"

if [ -f "$OUTPUT" ]; then
  echo "✅ Filtered and categorized $(grep -c '^#EXTINF' "$OUTPUT") channels."
else
  echo "❌ Error: $OUTPUT not found!"
  exit 1
fi

# Prepare Git for push
echo "📦 Committing and pushing to GitHub..."

# Add .gitignore for venv
echo "venv/" > .gitignore
git add .gitignore

# Stage the output file
git add "$OUTPUT"

# Only commit if there are actual changes
if ! git diff --cached --quiet; then
  git commit -m "Update filtered M3U playlist"
  git push
else
  echo "✅ No changes to commit."
fi

deactivate
