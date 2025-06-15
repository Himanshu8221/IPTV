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

# Run Python script
echo "🚀 Running script..."
python "code.py"

# Deactivate virtual environment
deactivate

echo "✅ Done!"
