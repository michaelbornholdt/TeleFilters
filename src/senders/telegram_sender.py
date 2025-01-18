from telethon import TelegramClient
import asyncio
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramSender:
    def __init__(self, client: TelegramClient):
        """Initialize sender with an existing client
        
        Args:
            client: An authenticated TelegramClient instance
        """
        self.client = client

    async def send_analyzed_messages(self, user_id: int, test_mode: bool = False):
        """Send analyzed messages to the user
        
        Args:
            user_id: User ID to send messages to
            test_mode: If True, only processes first 3 conversations
        """
        try:
            # Find latest analysis file
            analysis_dir = Path(f"users/{user_id}/analysis")
            if not analysis_dir.exists():
                logger.error("No analysis directory found")
                return
                
            analysis_files = list(analysis_dir.glob("filtered_*.json"))
            if not analysis_files:
                logger.error("No analysis files found")
                return
                
            # Get most recent analysis file
            latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"Using latest analysis file: {latest_file.name}")

            # Load analyzed data
            with open(latest_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)

            if not entries:
                logger.info("No relevant events found to send")
                return

            # Send header message
            me = await self.client.get_me()
            header = f"🔍 Event Updates ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            header += f"Found {len(entries)} relevant items:\n{'='*30}\n"
            await self.client.send_message(me.id, header)

            # Send each entry as a separate message
            for entry in entries:
                await self.client.send_message(me.id, entry)
                await asyncio.sleep(0.5)  # Small delay between messages
            
            logger.info(f"Successfully sent {len(entries)} messages")
            
        except Exception as e:
            logger.error(f"Failed to send messages: {str(e)}")