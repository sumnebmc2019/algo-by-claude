# telegram/helpers.py
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
        raise ValueError(f"No chat_id or chat_ids found in {bot_type} config")
    
    return {
        'bot_token': tg_config['bot_token'],
        'chat_ids': chat_ids
    }

def is_authorized_user(chat_id: Union[str, int], bot_type: str = "realtime") -> bool:
    """Check if chat_id is authorized to use the bot"""
    config = load_telegram_config(bot_type)
    chat_id_str = str(chat_id)
    return chat_id_str in [str(cid) for cid in config['chat_ids']]

def get_authorized_chat_ids(bot_type: str = "realtime") -> List[str]:
    """Get all authorized chat IDs"""
    config = load_telegram_config(bot_type)
    return [str(cid) for cid in config['chat_ids']]
