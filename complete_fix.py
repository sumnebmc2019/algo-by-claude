#!/usr/bin/env python
"""
Complete Fix Script for ALGO BY GUGAN
Fixes all issues from the conversation and optimizes the project
"""

import os
import sys
import shutil
from pathlib import Path
import re

class AlgoFixer:
    """Complete project fixer"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = []
        self.errors = []
    
    def print_header(self, text):
        """Print section header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def print_step(self, text):
        """Print step"""
        print(f"\n[STEP] {text}")
    
    def print_success(self, text):
        """Print success message"""
        print(f"  [OK] {text}")
        self.fixes_applied.append(text)
    
    def print_error(self, text):
        """Print error message"""
        print(f"  [ERROR] {text}")
        self.errors.append(text)
    
    def fix_emoji_in_files(self):
        """Remove emoji characters from all Python files"""
        self.print_step("Fixing emoji characters in code...")
        
        replacements = {
            '[OK]': '[OK]',
            '[ERROR]': '[ERROR]',
            '[WARNING]': '[WARNING]',
            '[WARNING]': '[WARNING]',
            '[INFO]': '[INFO]',
            '[START]': '[START]',
            '[STOP]': '[STOP]',
            '[STOP]': '[STOP]',
            'Rs.': 'Rs.',
            '': '',
            '': '',
            '': '',
            '': '',
            '[+]': '[+]',
            '[-]': '[-]',
            '[=]': '[=]',
        }
        
        files_fixed = 0
        
        for py_file in self.project_root.rglob('*.py'):
            # Skip virtual environment and cache
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace emojis
                for emoji, replacement in replacements.items():
                    content = content.replace(emoji, replacement)
                
                # Only write if changed
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_fixed += 1
                    
            except Exception as e:
                self.print_error(f"Error fixing {py_file}: {e}")
        
        self.print_success(f"Fixed emoji in {files_fixed} files")
    
    def fix_logger_encoding(self):
        """Fix logger to handle UTF-8 properly on Windows"""
        self.print_step("Fixing logger encoding...")
        
        logger_file = self.project_root / 'utils' / 'logger.py'
        
        if not logger_file.exists():
            self.print_error("utils/logger.py not found")
            return
        
        try:
            with open(logger_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already has UTF-8 fixes
            if 'reconfigure' in content and 'utf-8' in content:
                self.print_success("Logger already has UTF-8 fixes")
                return
            
            # Add UTF-8 fix for Windows
            if 'sys.platform == \'win32\'' not in content:
                # Find console handler section
                console_handler_pattern = r'(console_handler = logging\.StreamHandler\(sys\.stdout\))'
                
                utf8_fix = r'''\1
    console_handler.setLevel(logging.INFO)
    
    # Force UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            # Python < 3.7
            pass'''
                
                content = re.sub(console_handler_pattern, utf8_fix, content)
                
                with open(logger_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.print_success("Fixed logger UTF-8 encoding")
            else:
                self.print_success("Logger already has UTF-8 fixes")
                
        except Exception as e:
            self.print_error(f"Error fixing logger: {e}")
    
    def create_directory_structure(self):
        """Ensure all required directories exist"""
        self.print_step("Creating directory structure...")
        
        directories = [
            'config',
            'core',
            'strategies',
            'bots',
            'telegram',
            'tg',  # Alternative telegram folder
            'utils',
            'data/master_lists',
            'data/historical',
            'data/backtest_state',
            'logs/backtest',
            'logs/realtime',
            'trades'
        ]
        
        for directory in directories:
            path = self.project_root / directory
            path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py for Python packages
            if directory in ['core', 'strategies', 'bots', 'telegram', 'tg', 'utils']:
                init_file = path / '__init__.py'
                if not init_file.exists():
                    init_file.touch()
        
        self.print_success(f"Created {len(directories)} directories")
    
    def create_telegram_helpers(self):
        """Create telegram helpers module"""
        self.print_step("Creating telegram helpers...")
        
        # Create both telegram/ and tg/ directories
        for tg_dir_name in ['telegram', 'tg']:
            tg_dir = self.project_root / tg_dir_name
            tg_dir.mkdir(exist_ok=True)
            
            helpers_content = '''# {}/helpers.py
"""
Helper functions for telegram bots with multi-chat support
"""

import yaml
from typing import List, Union
from pathlib import Path

def load_telegram_config(bot_type: str = "realtime") -> dict:
    """Load telegram configuration with multi-chat support"""
    secrets_path = Path("config/secrets.yaml")
    
    with open(secrets_path, 'r') as f:
        secrets = yaml.safe_load(f)
    
    tg_config = secrets['telegram'][bot_type]
    
    # Handle both old single chat_id and new chat_ids list
    if 'chat_ids' in tg_config:
        chat_ids = tg_config['chat_ids']
        if isinstance(chat_ids, str):
            chat_ids = [chat_ids]
    elif 'chat_id' in tg_config:
        chat_ids = [tg_config['chat_id']]
    else:
        raise ValueError(f"No chat_id or chat_ids found in {{bot_type}} config")
    
    return {{
        'bot_token': tg_config['bot_token'],
        'chat_ids': chat_ids
    }}

def is_authorized_user(chat_id: Union[str, int], bot_type: str = "realtime") -> bool:
    """Check if chat_id is authorized to use the bot"""
    config = load_telegram_config(bot_type)
    chat_id_str = str(chat_id)
    return chat_id_str in [str(cid) for cid in config['chat_ids']]

def get_authorized_chat_ids(bot_type: str = "realtime") -> List[str]:
    """Get all authorized chat IDs"""
    config = load_telegram_config(bot_type)
    return [str(cid) for cid in config['chat_ids']]
'''.format(tg_dir_name)
            
            helpers_path = tg_dir / 'helpers.py'
            with open(helpers_path, 'w', encoding='utf-8') as f:
                f.write(helpers_content)
        
        self.print_success("Created telegram helpers")
    
    def update_gitignore(self):
        """Update .gitignore to protect sensitive data"""
        self.print_step("Updating .gitignore...")
        
        gitignore_additions = '''
# === ALGO BY GUGAN ===

# Secrets (NEVER commit these!)
config/secrets.yaml
.env
.env.local
.env.*.local

# Logs
logs/
*.log
*.log.*

# Historical Data (too large for git)
data/historical/
data/backtest_state/

# Trade Data
trades/*.csv

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''
        
        gitignore_path = self.project_root / '.gitignore'
        
        try:
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    current_content = f.read()
                
                if 'ALGO BY GUGAN' not in current_content:
                    with open(gitignore_path, 'a') as f:
                        f.write(gitignore_additions)
                    self.print_success("Updated .gitignore")
                else:
                    self.print_success(".gitignore already updated")
            else:
                with open(gitignore_path, 'w') as f:
                    f.write(gitignore_additions)
                self.print_success("Created .gitignore")
                
        except Exception as e:
            self.print_error(f"Error updating .gitignore: {e}")
    
    def create_deployment_files(self):
        """Create files for Railway deployment"""
        self.print_step("Creating deployment files...")
        
        # railway.json
        railway_json = '''{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}'''
        
        # Procfile
        procfile = '''web: python run_realtime.py
worker: python run_backtest.py
'''
        
        # nixpacks.toml
        nixpacks = '''[phases.setup]
nixPkgs = ["python310"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "python run_realtime.py"
'''
        
        # runtime.txt for Heroku/other platforms
        runtime = 'python-3.11.0\n'
        
        files = {
            'railway.json': railway_json,
            'Procfile': procfile,
            'nixpacks.toml': nixpacks,
            'runtime.txt': runtime
        }
        
        for filename, content in files.items():
            file_path = self.project_root / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        self.print_success(f"Created {len(files)} deployment files")
    
    def create_env_template(self):
        """Create .env.template for environment variables"""
        self.print_step("Creating .env.template...")
        
        env_template = '''# ALGO BY GUGAN - Environment Variables Template
# Copy this to .env and fill in your values
# NEVER commit .env to git!

# Telegram Configuration
TELEGRAM_REALTIME_TOKEN=your_realtime_bot_token_from_botfather
TELEGRAM_REALTIME_CHAT_IDS=your_chat_id_1,your_chat_id_2,your_chat_id_3
TELEGRAM_BACKTEST_TOKEN=your_backtest_bot_token_from_botfather
TELEGRAM_BACKTEST_CHAT_IDS=your_chat_id_1,your_chat_id_2

# AngelOne Configuration
ANGELONE_API_KEY=your_angelone_api_key
ANGELONE_CLIENT_ID=your_angelone_client_id
ANGELONE_PASSWORD=your_angelone_password
ANGELONE_TOTP_SECRET=your_angelone_totp_secret
ANGELONE_ENABLED=true

# Zerodha Configuration (optional)
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret
ZERODHA_ENABLED=false

# Deployment
RAILWAY_ENVIRONMENT=production
'''
        
        env_template_path = self.project_root / '.env.template'
        with open(env_template_path, 'w', encoding='utf-8') as f:
            f.write(env_template)
        
        self.print_success("Created .env.template")
    
    def verify_requirements(self):
        """Verify requirements.txt has all needed packages"""
        self.print_step("Verifying requirements.txt...")
        
        required_packages = [
            'python-telegram-bot==20.7',
            'pyyaml==6.0.1',
            'pandas==2.1.4',
            'numpy==1.26.2',
            'pytz==2023.3',
            'requests==2.31.0',
            'python-dotenv==1.0.0',
            'schedule==1.2.0',
            'smartapi-python==1.3.0',
            'pyotp==2.9.0',
            'logzero==1.7.0',
            'websocket-client==1.8.0'
        ]
        
        req_file = self.project_root / 'requirements.txt'
        
        if req_file.exists():
            with open(req_file, 'r') as f:
                current_packages = set(line.strip() for line in f if line.strip())
            
            missing = set(required_packages) - current_packages
            
            if missing:
                with open(req_file, 'a') as f:
                    f.write('\n# Added by fix script\n')
                    for package in missing:
                        f.write(f'{package}\n')
                self.print_success(f"Added {len(missing)} missing packages")
            else:
                self.print_success("All packages present")
        else:
            with open(req_file, 'w') as f:
                f.write('\n'.join(required_packages))
            self.print_success("Created requirements.txt")
    
    def create_quick_start_script(self):
        """Create quick start script"""
        self.print_step("Creating quick start scripts...")
        
        # start_bots.sh (Linux/Mac)
        start_sh = '''#!/bin/bash
# ALGO BY GUGAN - Quick Start Script

echo "Starting ALGO BY GUGAN..."

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run setup
python setup_angelone.py

# Start both bots in tmux
tmux new-session -d -s algo_realtime 'python run_realtime.py'
tmux new-session -d -s algo_backtest 'python run_backtest.py'

echo "Bots started!"
echo "View realtime: tmux attach -t algo_realtime"
echo "View backtest: tmux attach -t algo_backtest"
echo "Detach from tmux: Ctrl+B then D"
'''
        
        # start_bots.bat (Windows)
        start_bat = '''@echo off
REM ALGO BY GUGAN - Quick Start Script (Windows)

echo Starting ALGO BY GUGAN...

REM Activate virtual environment
call .venv\\Scripts\\activate.bat

REM Install/update dependencies
pip install -r requirements.txt

REM Run setup
python setup_angelone.py

REM Start realtime bot
start "Realtime Bot" python run_realtime.py

REM Start backtest bot
start "Backtest Bot" python run_backtest.py

echo Bots started in separate windows!
pause
'''
        
        # Save scripts
        sh_path = self.project_root / 'start_bots.sh'
        with open(sh_path, 'w', encoding='utf-8') as f:
            f.write(start_sh)
        
        # Make executable on Unix
        try:
            os.chmod(sh_path, 0o755)
        except:
            pass
        
        bat_path = self.project_root / 'start_bots.bat'
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(start_bat)
        
        self.print_success("Created quick start scripts")
    
    def create_test_telegram_script(self):
        """Create telegram test script"""
        self.print_step("Creating telegram test script...")
        
        test_script = '''#!/usr/bin/env python
"""
Test Telegram Bot Connection
"""

import asyncio
import yaml
from telegram import Bot

async def test_telegram():
    """Test telegram configuration"""
    print("=" * 60)
    print("Testing Telegram Bot Configuration")
    print("=" * 60)
    
    try:
        # Load config
        with open('config/secrets.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Test realtime bot
        print("\\n1. Testing Realtime Bot...")
        rt_config = config['telegram']['realtime']
        rt_token = rt_config['bot_token']
        
        # Get chat IDs
        if 'chat_ids' in rt_config:
            rt_chat_ids = rt_config['chat_ids']
        else:
            rt_chat_ids = [rt_config['chat_id']]
        
        print(f"   Token: {rt_token[:10]}...")
        print(f"   Chat IDs: {rt_chat_ids}")
        
        # Create bot
        rt_bot = Bot(token=rt_token)
        
        # Get bot info
        me = await rt_bot.get_me()
        print(f"   Bot: @{me.username} ({me.first_name})")
        
        # Send test messages
        for chat_id in rt_chat_ids:
            try:
                msg = await rt_bot.send_message(
                    chat_id=chat_id,
                    text="[TEST] Realtime bot is working!"
                )
                print(f"   [OK] Sent to {chat_id}")
            except Exception as e:
                print(f"   [ERROR] Failed to send to {chat_id}: {e}")
        
        # Test backtest bot
        print("\\n2. Testing Backtest Bot...")
        bt_config = config['telegram']['backtest']
        bt_token = bt_config['bot_token']
        
        if 'chat_ids' in bt_config:
            bt_chat_ids = bt_config['chat_ids']
        else:
            bt_chat_ids = [bt_config['chat_id']]
        
        print(f"   Token: {bt_token[:10]}...")
        print(f"   Chat IDs: {bt_chat_ids}")
        
        bt_bot = Bot(token=bt_token)
        me = await bt_bot.get_me()
        print(f"   Bot: @{me.username} ({me.first_name})")
        
        for chat_id in bt_chat_ids:
            try:
                msg = await bt_bot.send_message(
                    chat_id=chat_id,
                    text="[TEST] Backtest bot is working!"
                )
                print(f"   [OK] Sent to {chat_id}")
            except Exception as e:
                print(f"   [ERROR] Failed to send to {chat_id}: {e}")
        
        print("\\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)
        
    except FileNotFoundError:
        print("[ERROR] config/secrets.yaml not found!")
        print("Create it using the template in .env.template")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram())
'''
        
        test_path = self.project_root / 'test_telegram.py'
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        self.print_success("Created test_telegram.py")
    
    def generate_report(self):
        """Generate fix report"""
        self.print_header("FIX REPORT")
        
        print(f"\n[SUCCESS] Applied {len(self.fixes_applied)} fixes:")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"  {i}. {fix}")
        
        if self.errors:
            print(f"\n[WARNING] {len(self.errors)} errors occurred:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("\n1. Update config/secrets.yaml with your credentials")
        print("2. Run: python test_telegram.py")
        print("3. Run: python setup_angelone.py")
        print("4. Test locally: python run_realtime.py")
        print("5. Deploy to Railway/Oracle Cloud")
        print("\nFor deployment:")
        print("- Railway: Push to GitHub and deploy")
        print("- Oracle Cloud: Use deployment guide")
        print()
    
    def run_all_fixes(self):
        """Run all fixes"""
        self.print_header("ALGO BY GUGAN - Complete Fix Script")
        
        # Run all fix methods
        self.create_directory_structure()
        self.fix_emoji_in_files()
        self.fix_logger_encoding()
        self.create_telegram_helpers()
        self.update_gitignore()
        self.create_deployment_files()
        self.create_env_template()
        self.verify_requirements()
        self.create_quick_start_script()
        self.create_test_telegram_script()
        
        # Generate report
        self.generate_report()

def main():
    """Main entry point"""
    fixer = AlgoFixer()
    fixer.run_all_fixes()

if __name__ == "__main__":
    main()