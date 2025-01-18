from pathlib import Path
import json
from datetime import datetime
import getpass
import logging

class UserManager:
    def __init__(self, base_path="users"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def setup_new_user(self, user_id: str) -> Path:
        """Interactive setup for a new user"""
        print("\n=== New User Setup ===")
        print("Please enter your Telegram API credentials.")
        print("You can get these from https://my.telegram.org/apps")
        
        # Get credentials
        api_id = input("Enter your API ID: ").strip()
        api_hash = getpass.getpass("Enter your API hash: ").strip()
        phone = input("Enter your phone number (with country code, e.g. +1234567890): ").strip()
        
        # Validate inputs
        if not api_id.isdigit():
            raise ValueError("API ID must be a number")
        if not phone.startswith("+"):
            raise ValueError("Phone number must start with + and include country code")
        
        # Create user directory
        user_path = self.base_path / str(api_id)
        user_path.mkdir(exist_ok=True)
        
        # Create user-specific config.py
        config_content = f'''# Telegram API Credentials
TELEGRAM_API_ID = {api_id}
TELEGRAM_API_HASH = "{api_hash}"
TELEGRAM_PHONE = "{phone}"
CREATED_AT: {str(datetime.now())}
ACTIVE: True
'''
        
        with open(user_path / "config.py", "w") as f:
            f.write(config_content)
        
        print(f"\nSuccessfully created user configuration at {user_path}")
        print("You can now run the bot with --fetch, --analyze, or --send options")
        
        return user_path
    
    def get_user_session_path(self, user_id: str) -> Path:
        """Returns path where Telethon should store session file"""
        return self.base_path / str(user_id) / f"user_{user_id}.session"
    
    def list_users(self) -> list:
        """List all active users"""
        return [d.name for d in self.base_path.iterdir() if d.is_dir()]
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user directory exists"""
        return (self.base_path / str(user_id)).exists() 