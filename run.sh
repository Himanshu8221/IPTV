#!/data/data/com.termux/files/usr/bin/bash

# Exit if any command fails
set -e

echo "📦 Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python -m venv venv
fi

# Activate the virtual environment
. venv/bin/activate

# Install Python dependencies
pip install -q -r requirements.txt

# No need to export M3U_URL — .env will handle it

# Run the Python script
echo "🚀 Running IPTV channel fetch + filter script..."
python code.py

# Deactivate the virtual environment
deactivate

echo "✅ Done!"
