#!/bin/bash

# Set script to exit if any command fails
set -e

echo "📦 Setting up environment..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate virtual environment
source . venv/bin/activate

# Install required packages
pip install -q -r requirements.txt || pip install -q python-dotenv requests

# Optional: Export M3U_URL for GitHub Actions or local override
export M3U_URL="http://starshare.org:80/get.php?username=gurmeet&password=gurmeet&type=m3u_plus&output=mpegts"

# Run Python script
echo "🚀 Running Python script..."
python3 "code for all links.py"

# Deactivate virtual environment
deactivate

echo "✅ Script execution complete."
