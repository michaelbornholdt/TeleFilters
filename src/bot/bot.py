import os
import sys
from pathlib import Path
import nest_asyncio
import asyncio
from telethon import TelegramClient
import json
from datetime import datetime, timezone, timedelta
import logging
import argparse

# Get the absolute path to the telegram_bot directory (root)
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import configuration
from config.config import (
    TELEGRAM_API_ID as API_ID,
    TELEGRAM_API_HASH as API_HASH,
    TELEGRAM_PHONE as PHONE_NUMBER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    RELEVANT_CATEGORIES,
    IRRELEVANT_TOPICS,
    SESSION_NAME,
)

# Import crawler and analyzer
from src.crawlers.telegram_crawler import process_dialogs
from src.analyzers.conversation_filter import ConversationAnalyzer
from src.senders.telegram_sender import TelegramSender
from src.user_manager import UserManager

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

def configure_logging(log_level='INFO'):
    """Configure logging settings with cleaner output"""
    # Remove any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create clean formatter without timestamp
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger('telethon.network').setLevel(logging.WARNING)
    logging.getLogger('telethon.extensions').setLevel(logging.WARNING)
    logging.getLogger('telethon.crypto').setLevel(logging.WARNING)
    logging.getLogger('telethon.connection').setLevel(logging.WARNING)
    logging.getLogger('telethon.client').setLevel(logging.WARNING)
    
    # Set handlers.message_processor logger level to INFO
    logging.getLogger('handlers.message_processor').setLevel(logging.INFO)
    
    # Set root logger level
    root_logger.setLevel(log_level)

def run_bot():
    parser = argparse.ArgumentParser(description='Telegram Bot')
    parser.add_argument('--user-id', type=int, required=False,
                       help='Target user\'s Telegram ID (numeric)')
    parser.add_argument('--setup', action='store_true',
                       help='Setup a new user interactively')
    parser.add_argument('-c', '--connect', action='store_true',
                       help='Connect to Telegram')
    parser.add_argument('-f', '--fetch', action='store_true',
                       help='Fetch messages from channels')
    parser.add_argument('-a', '--analyze', action='store_true',
                       help='Analyze the latest messages file')
    parser.add_argument('-t', '--test', action='store_true',
                       help='Run in test mode (limited processing)')
    parser.add_argument('-s', '--send', action='store_true',
                       help='Send analyzed messages to user')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Set the logging level')
    args = parser.parse_args()
    
    # Configure logging with clean output
    configure_logging(args.log_level)
    
    user_manager = UserManager()
    
    # Handle user setup
    if args.setup or not args.user_id:
        try:
            user_manager.setup_new_user(str(args.user_id))
            return
        except Exception as e:
            logging.error(f"Failed to setup user: {e}")
            return
    
    # Check if user exists before proceeding
    if not user_manager.user_exists(str(args.user_id)):
        logging.error(f"User {args.user_id} does not exist. Please run with --setup first")
        return
    
    if args.test:
        logging.debug("Running in TEST MODE")
    
    bot = TelegramBot(target_user_id=args.user_id)
    return asyncio.run(bot.main(args))

class TelegramBot:
    def __init__(self, target_user_id: int):
        self.target_user_id = target_user_id
        self.user_dir = Path("users") / str(target_user_id)
        self.temperature = OPENAI_TEMPERATURE
        
        # Load user's config
        self.load_user_config()
        
        # Initialize client with user-specific session path
        session_path = self.user_dir / f"user_{target_user_id}_session"
        self.client = TelegramClient(
            str(session_path),  # Convert Path to string for Telethon
            self.api_id, 
            self.api_hash
        )

    def load_user_config(self):
        """Load credentials from user's config.py file"""
        config_file = self.user_dir / "config.py"
        
        if not config_file.exists():
            raise ValueError(f"No config found for user {self.target_user_id}. Please set up user first.")
        
        # Add user directory to Python path temporarily
        sys.path.insert(0, str(self.user_dir.parent))
        
        try:
            # Import user's config module
            user_config = __import__(f"{self.target_user_id}.config")
            
            # Extract credentials
            self.api_id = user_config.config.TELEGRAM_API_ID
            self.api_hash = user_config.config.TELEGRAM_API_HASH
            self.phone = user_config.config.TELEGRAM_PHONE
            
        finally:
            # Remove user directory from Python path
            sys.path.pop(0)

    async def start(self):
        """Connect and authenticate with Telegram"""
        if not self.client.is_connected():
            print("Connecting to Telegram...")
            await self.client.connect()
            
        if not await self.client.is_user_authorized():
            print("Need to authorize...")
            await self.client.start(phone=self.phone)
        
        # Get and log user info
        me = await self.client.get_me()
        username = me.username or me.first_name or str(me.id)
        logging.info(f"Connected as user: {username} (ID: {me.id})")

    async def send_analyzed_messages(self, test_mode: bool = False):
        """Send analyzed messages to output channel
        
        Args:
            test_mode: Ignored, kept for consistency with other methods
        """
        if test_mode:
            logging.info("Running sending in TEST MODE - only processing first 3 conversations")
        logging.info("Starting to send messages...")
        try:
                
            # Create sender with existing client
            sender = TelegramSender(self.client)
            await sender.send_analyzed_messages(self.target_user_id, test_mode=test_mode)
            
        except Exception as e:
            logging.error(f"Failed to send messages: {str(e)}")

    async def fetch_messages(self, test_mode: bool = False):
        """Fetch messages and save to user directory"""
        logging.info("Starting to fetch messages...")
        try:
            # Get current time and 24 hours ago for the date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            # Create messages directory if it doesn't exist
            messages_dir = self.user_dir / "messages"
            messages_dir.mkdir(exist_ok=True)
            
            # Get authenticated user's name
            me = await self.client.get_me()
            user_name = me.first_name or str(self.target_user_id)
            
            # Create a more readable timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            
            # Create a more descriptive filename
            output_file = messages_dir / f"messages_{timestamp}.json"
            
            # Use the process_dialogs function
            messages = await process_dialogs(
                self.client,
                start_date=start_date,
                end_date=end_date, 
                test_mode=test_mode
            )
            
            # Save the messages to the user directory
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)

            logging.info(f"\n=== Done Fetching Messages! ===")   
            logging.info(f"Successfully saved messages to {output_file}")
            logging.info(f"Total chats processed: {messages['metadata']['total_chats_processed']}")
            logging.info(f"Total messages: {messages['metadata']['total_messages']}")
            
        except Exception as e:
            logging.error(f"Error fetching messages: {str(e)}")

    async def analyze_messages(self, test_mode: bool = False):
        """Analyze fetched messages"""
        if test_mode:
            logging.info("Running analysis in TEST MODE - only processing first 3 conversations")
        logging.info("Starting message analysis...\n ----- ")
        
        try: 
            # Initialize analyzer
            analyzer = ConversationAnalyzer(
                api_key=OPENAI_API_KEY,
                model=OPENAI_MODEL,
                temperature=self.temperature
            )
            
            # Run analysis with test mode - file handling is now done in ConversationAnalyzer
            await analyzer.analyze_conversations(self.target_user_id, test_mode=test_mode)
            
        except Exception as e:
            logging.error(f"Error analyzing messages: {str(e)}")
            raise  # Re-raise to show full error trace

    async def main(self, args):
        """Main entry point for bot operations"""
        try:
            if args.connect or not self.client.is_connected():
                await self.start()

            if args.fetch:
                await self.fetch_messages(test_mode=args.test)
                
            if args.analyze:
                await self.analyze_messages(test_mode=args.test)
            
            if args.send:
                await self.send_analyzed_messages(test_mode=args.test)
                
        except Exception as e:
            logging.error(f"Error in main: {str(e)}")
            raise


if __name__ == "__main__":
    run_bot()
