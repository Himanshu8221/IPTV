#!/bin/sh

# Exit immediately if a command fails
set -e

echo "📦 Setting up environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python -m venv venv
fi

# Activate virtual environment (use . instead of source)
. venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt || pip install -q requests python-dotenv

# Optional: export M3U_URL if not using .env
export M3U_URL="http://starshare.org:80/get.php?username=gurmeet&password=gurmeet&type=m3u_plus&output=mpegts"

# Run Python script
echo "🚀 Running script..."
python "code for all links.py"

# Deactivate virtual environment
deactivate

echo "✅ Done!"
