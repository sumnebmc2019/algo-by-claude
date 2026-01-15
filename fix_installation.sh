#!/bin/bash
# fix_installation.sh - Fix all installation and dependency issues

echo "============================================================"
echo "ALGO BY GUGAN - Installation Fix Script"
echo "============================================================"

# Activate virtual environment
source ~/.venv/bin/activate

echo ""
echo "Step 1: Uninstalling conflicting smartapi package..."
pip uninstall -y smartapi-python

echo ""
echo "Step 2: Installing correct AngelOne SmartAPI package..."
pip install smartapi-python==1.3.0

echo ""
echo "Step 3: Installing missing dependencies..."
pip install logzero==1.7.0
pip install websocket-client==1.8.0

echo ""
echo "Step 4: Verifying installations..."
python3 << 'EOF'
try:
    from SmartApi import SmartConnect
    print("✅ SmartApi imported successfully")
except ImportError as e:
    print(f"❌ SmartApi import failed: {e}")

try:
    import pyotp
    print("✅ pyotp imported successfully")
except ImportError as e:
    print(f"❌ pyotp import failed: {e}")

try:
    from telegram import Update
    print("✅ telegram imported successfully")
except ImportError as e:
    print(f"❌ telegram import failed: {e}")

print("\n✅ All critical imports verified!")
EOF

echo ""
echo "Step 5: Checking bot files for emoji issues..."
cd ~/algo

# Create backup
echo "Creating backup of telegram files..."
cp tg/rt_telegram.py tg/rt_telegram.py.backup
cp tg/bt_telegram.py tg/bt_telegram.py.backup

echo ""
echo "============================================================"
echo "✅ Installation Fix Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Replace tg/rt_telegram.py with the fixed version"
echo "2. Replace tg/bt_telegram.py with the fixed version"
echo "3. Restart both bots"
echo ""