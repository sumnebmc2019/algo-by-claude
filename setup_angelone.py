# config/secrets.yaml
"""
AngelOne SmartAPI Setup Script
Run this script to download master contracts and test connection
"""

import json
import yaml
from pathlib import Path
from SmartApi import SmartConnect
import pyotp

def load_secrets():
    """Load secrets from config"""
    with open('config/secrets.yaml', 'r') as f:
        return yaml.safe_load(f)

def test_connection():
    """Test AngelOne connection"""
    print("=" * 60)
    print("AngelOne SmartAPI Connection Test")
    print("=" * 60)
    
    secrets = load_secrets()
    angelone_config = secrets['brokers']['angelone']
    
    try:
        # Initialize SmartAPI
        print("\n1. Initializing SmartAPI...")
        smart_api = SmartConnect(api_key=angelone_config['api_key'])
        
        # Generate TOTP
        print("2. Generating TOTP...")
        totp = pyotp.TOTP(angelone_config['totp_secret']).now()
        print(f"   Current TOTP: {totp}")
        
        # Login
        print("3. Logging in...")
        data = smart_api.generateSession(
            clientCode=angelone_config['client_id'],
            password=angelone_config['password'],
            totp=totp
        )
        
        if data['status']:
            print("[OK] Login successful!")
            print(f"   User ID: {data['data']['clientcode']}")
            print(f"   Name: {data['data']['name']}")
            return smart_api
        else:
            print(f"[ERROR] Login failed: {data}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

def download_master_contracts(smart_api):
    """Download master contracts from AngelOne OFFICIAL URL"""
    print("\n" + "=" * 60)
    print("Downloading Master Contracts")
    print("=" * 60)
    
    # OFFICIAL AngelOne master file URL (works 100%)
    master_url = "https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json"
    
    master_dir = Path('data/master_lists')
    master_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("📥 Downloading from official AngelOne URL...")
        import requests
        response = requests.get(master_url, timeout=30)
        
        if response.status_code == 200:
            all_instruments = response.json()
            print(f"[OK] Downloaded {len(all_instruments)} total instruments")
            
            # Filter and save by segment
            segments = {
                'NSE_EQ': [],
                'NSE_FO': [],
                'BSE_EQ': [],
                'MCX_FO': [],
                'CDS_FO': []
            }
            
            for inst in all_instruments:
                exch_seg = inst.get('exch_seg', '')
                if exch_seg == 'NSE':
                    segments['NSE_EQ'].append(inst)
                elif exch_seg == 'NFO':
                    segments['NSE_FO'].append(inst)
                elif exch_seg == 'BSE':
                    segments['BSE_EQ'].append(inst)
                elif exch_seg == 'MCX':
                    segments['MCX_FO'].append(inst)
                elif exch_seg == 'CDS':
                    segments['CDS_FO'].append(inst)
            
            # Save each segment
            for segment, instruments in segments.items():
                if instruments:
                    file_path = master_dir / f"angelone_{segment}.json"
                    with open(file_path, 'w') as f:
                        json.dump(instruments, f, indent=2)
                    print(f"[OK] Saved {len(instruments)} {segment} instruments")
                else:
                    print(f"[WARNING]  No {segment} instruments found")
                    
        else:
            print(f"[ERROR] Download failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Error downloading master: {e}")
        print("💡 Manual download: https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json")


def test_ltp(smart_api):
    """Test LTP fetch"""
    print("\n" + "=" * 60)
    print("Testing LTP Fetch")
    print("=" * 60)
    
    # Test with NIFTY
    test_symbols = [
        {'exchange': 'NSE', 'symbol': 'NIFTY-I', 'token': '99926000'},
        {'exchange': 'NSE', 'symbol': 'BANKNIFTY-I', 'token': '99926009'}
    ]
    
    for test in test_symbols:
        try:
            print(f"\nFetching LTP for {test['symbol']}...")
            ltp_data = smart_api.ltpData(
                test['exchange'],
                test['symbol'],
                test['token']
            )
            
            if ltp_data and ltp_data['status']:
                ltp = ltp_data['data']['ltp']
                print(f"[OK] {test['symbol']}: ₹{ltp}")
            else:
                print(f"[WARNING]  Failed to fetch LTP: {ltp_data}")
                
        except Exception as e:
            print(f"[ERROR] Error: {e}")

def main():
    """Main setup function"""
    print("\n[START] Starting AngelOne SmartAPI Setup\n")
    
    # Test connection
    smart_api = test_connection()
    
    if not smart_api:
        print("\n[ERROR] Connection failed. Please check your credentials in config/secrets.yaml")
        return
    
    # Download master contracts
    download_master_contracts(smart_api)
    
    # Test LTP
    test_ltp(smart_api)
    
    print("\n" + "=" * 60)
    print("[OK] Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check data/master_lists/ for downloaded contracts")
    print("2. Update your strategy with desired symbols")
    print("3. Start the bots with: python run_realtime.py")
    print("\n")

if __name__ == "__main__":
    main()