#!/usr/bin/env python
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
        print("\n1. Testing Realtime Bot...")
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
        print("\n2. Testing Backtest Bot...")
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
        
        print("\n" + "=" * 60)
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
