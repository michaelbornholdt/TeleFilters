from datetime import datetime
from pathlib import Path


class UserManager:
    def __init__(
        self,
        # base_path: str = "s3://infrastructurestack-userdata6a2e227b-jjxpj68kosc9/users/",
        base_path: str = "/home/miha/TeleFilters/users",
    ):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    def setup_new_user(self, api_id: int, api_hash: str, phone_number: str) -> Path:
        """Setup new user"""

        # Validate inputs
        if not api_id.isdigit():
            raise ValueError("API ID must be a number")
        if not phone_number.startswith("+"):
            raise ValueError("Phone number must start with + and include country code")

        # Create user directory
        user_path = self.base_path / str(api_id)
        user_path.mkdir(exist_ok=True)

        # Create user-specific config json
        config_content = {
            "TELEGRAM_API_ID": api_id,
            "TELEGRAM_API_HASH": api_hash,
            "TELEGRAM_PHONE": phone_number,
            "CREATED_AT": str(datetime.now()),
            "ACTIVE": True,
        }
        import json

        with open(user_path / "config.json", "w") as f:
            json.dump(config_content, f, indent=4)

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


if __name__ == "__main__":
    import os

    from telethon.sync import TelegramClient

    um = UserManager()
    um.setup_new_user(
        api_id=os.getenv("TELEGRAM_API_ID"),
        api_hash=os.getenv("TELEGRAM_API_KEY"),
        phone_number="+38640737782",
    )

    # session_path = um.get_user_session_path("14242555")

    client = TelegramClient(
        str("session_path"),  # Convert Path to string for Telethon
        api_id=os.getenv("TELEGRAM_API_ID"),
        api_hash=os.getenv("TELEGRAM_API_KEY"),
    )
