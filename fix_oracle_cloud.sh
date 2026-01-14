#!/bin/bash
# Oracle Cloud Network Fix Script for ALGO BY GUGAN

echo "============================================"
echo "Oracle Cloud Network Fix for AngelOne API"
echo "============================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root: sudo bash fix_oracle_cloud.sh"
    exit 1
fi

echo ""
echo "📋 Current Network Configuration:"
echo "================================="

# Show current iptables rules
echo ""
echo "1. Current iptables rules:"
iptables -L -n | head -20

# Check DNS resolution
echo ""
echo "2. Testing DNS resolution for apiconnect.angelone.in:"
nslookup apiconnect.angelone.in || echo "❌ DNS resolution failed"

# Check connectivity
echo ""
echo "3. Testing connection to AngelOne API:"
timeout 10 curl -v https://apiconnect.angelone.in 2>&1 | head -20 || echo "❌ Connection failed"

echo ""
echo "============================================"
echo "🔧 Applying Fixes..."
echo "============================================"

# Fix 1: Allow outbound HTTPS
echo ""
echo "1. Allowing outbound HTTPS (port 443)..."
iptables -I OUTPUT -p tcp --dport 443 -j ACCEPT
iptables -I OUTPUT -p tcp --dport 80 -j ACCEPT
echo "✅ Outbound HTTPS allowed"

# Fix 2: Allow established connections
echo ""
echo "2. Allowing established connections..."
iptables -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -I OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
echo "✅ Established connections allowed"

# Fix 3: Allow DNS
echo ""
echo "3. Allowing DNS queries..."
iptables -I OUTPUT -p udp --dport 53 -j ACCEPT
iptables -I INPUT -p udp --sport 53 -j ACCEPT
echo "✅ DNS allowed"

# Fix 4: Save iptables rules
echo ""
echo "4. Saving iptables rules..."
if command -v iptables-save &> /dev/null; then
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || {
        mkdir -p /etc/iptables
        iptables-save > /etc/iptables/rules.v4
    }
    echo "✅ Rules saved to /etc/iptables/rules.v4"
else
    echo "⚠️  iptables-save not found, rules won't persist after reboot"
fi

# Fix 5: Install iptables-persistent (for Ubuntu)
echo ""
echo "5. Installing iptables-persistent..."
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent &>/dev/null
echo "✅ iptables-persistent installed"

# Fix 6: Configure Oracle Cloud specific settings
echo ""
echo "6. Configuring Oracle Cloud specific settings..."

# Disable Oracle Cloud firewall temporarily for testing
if systemctl is-active --quiet oracle-cloud-agent; then
    echo "⚠️  Oracle Cloud Agent detected"
    systemctl stop oracle-cloud-agent
    systemctl disable oracle-cloud-agent
    echo "✅ Oracle Cloud Agent disabled (can re-enable later if needed)"
fi

# Fix 7: Update MTU for Oracle Cloud
echo ""
echo "7. Updating MTU settings..."
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)
if [ ! -z "$INTERFACE" ]; then
    ip link set dev $INTERFACE mtu 1500
    echo "✅ MTU set to 1500 on $INTERFACE"
fi

# Fix 8: Add Google DNS as backup
echo ""
echo "8. Adding Google DNS as backup..."
if ! grep -q "8.8.8.8" /etc/resolv.conf; then
    echo "nameserver 8.8.8.8" >> /etc/resolv.conf
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf
    echo "✅ Google DNS added"
else
    echo "✅ Google DNS already present"
fi

echo ""
echo "============================================"
echo "🧪 Testing After Fixes..."
echo "============================================"

# Test DNS again
echo ""
echo "1. Testing DNS resolution:"
nslookup apiconnect.angelone.in && echo "✅ DNS working" || echo "❌ DNS still failing"

# Test connection
echo ""
echo "2. Testing HTTPS connection:"
timeout 10 curl -I https://apiconnect.angelone.in 2>&1 | grep -i "HTTP" && echo "✅ Connection working" || echo "❌ Connection still failing"

# Test with Python
echo ""
echo "3. Testing with Python requests:"
python3 -c "
import requests
import socket

# Set longer timeout
socket.setdefaulttimeout(30)

try:
    response = requests.get('https://apiconnect.angelone.in', timeout=30)
    print('✅ Python requests working')
    print(f'Status: {response.status_code}')
except Exception as e:
    print(f'❌ Python requests failed: {e}')
"

echo ""
echo "============================================"
echo "📝 Summary and Next Steps"
echo "============================================"
echo ""
echo "Fixes applied:"
echo "  ✅ Allowed outbound HTTPS (port 443)"
echo "  ✅ Allowed DNS queries"
echo "  ✅ Configured established connections"
echo "  ✅ Saved iptables rules"
echo "  ✅ Installed iptables-persistent"
echo "  ✅ Updated MTU settings"
echo "  ✅ Added backup DNS servers"
echo ""
echo "Next steps:"
echo "  1. Run: cd ~/algo && source .venv/bin/activate"
echo "  2. Test: python setup_angelone.py"
echo "  3. If still failing, check Oracle Cloud Console:"
echo "     - Networking → Security Lists → Add Egress Rule"
echo "     - Destination: 0.0.0.0/0, Protocol: TCP, Port: 443"
echo ""
echo "Additional troubleshooting:"
echo "  - View current rules: sudo iptables -L -n"
echo "  - Test connection: curl -v https://apiconnect.angelone.in"
echo "  - Check logs: journalctl -xe"
echo ""
echo "If issues persist, the problem might be:"
echo "  1. Oracle Cloud Security List (requires web console access)"
echo "  2. Subnet route table configuration"
echo "  3. Network Security Group (NSG) rules"
echo ""
echo "============================================"