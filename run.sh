#!/data/data/com.termux/files/usr/bin/bash

echo "📦 Installing Python requirements..."
pip install -r requirements.txt

echo "🚀 Running IPTV channel fetch + filter script..."
python3 code.py

OUTPUT="list.m3u"

if [ -f "$OUTPUT" ]; then
  echo "✅ Filtered and categorized $(grep -c '^#EXTINF' "$OUTPUT") channels."
else
  echo "❌ Error: $OUTPUT not found!"
  exit 1
fi

echo "📦 Preparing Git commit..."

# Add .gitignore for safety
echo "venv/" > .gitignore
git add .gitignore

# Stage output file
git add "$OUTPUT"

# Commit and push if there are changes
if ! git diff --cached --quiet; then
  git commit -m "Update filtered M3U playlist"
  echo "🚀 Pushing to GitHub..."
  git push
else
  echo "✅ No changes to commit."
fi
