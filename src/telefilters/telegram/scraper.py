from datetime import datetime, date, timezone, timedelta
from telethon import TelegramClient
from telethon.tl.types import Channel
from telethon.tl.functions.channels import GetForumTopicsRequest
from collections import OrderedDict
from typing import Dict, List, Any, Optional, Tuple


def scrape_messages(client: TelegramClient):
        """Fetch messages and save to user directory"""
            
        # Use the process_dialogs function
        messages = process_dialogs(client) 
        messages = messages[:100]
        return messages
        


# Configuration constants
MAX_DIALOGS = 100  # Maximum number of dialogs to process
MAX_MESSAGES_PER_DIALOG = 100  # Maximum messages to fetch per dialog/topic
ARCHIVED_FOLDER_ID = 1  # ID for archived folders
TEST_MODE_DIALOG_LIMIT = 10  # Number of dialogs to process in test mode

def should_stop_processing(
    dialog: Any,
    dialog_date: date,
    start_date: date,
    is_24h_query: bool,
    checked_count: int
) -> bool:
    """
    Determines if we should stop processing more dialogs based on efficiency rules.
    
    Args:
        dialog: The current dialog being processed
        dialog_date: Date of the last message in the dialog
        start_date: Start of the query date range
        is_24h_query: Whether this is a 24-hour query
        checked_count: Number of dialogs checked so far
        
    Returns:
        True if processing should stop, False otherwise
    """
    if isinstance(dialog_date, datetime):
        dialog_date = dialog_date.replace(tzinfo=timezone.utc)
    if isinstance(start_date, datetime):
        start_date = start_date.replace(tzinfo=timezone.utc)

    if is_24h_query and dialog_date < (start_date - timedelta(hours=25)) and not dialog.pinned:
        return True
    return False

def is_valid_dialog(dialog: Any) -> bool:
    """
    Checks if a dialog should be processed or skipped.
    
    Args:
        dialog: Dialog to check
        
    Returns:
        True if dialog should be processed, False if it should be skipped
    """
    if dialog.folder_id == ARCHIVED_FOLDER_ID:
        return False
    return True

async def fetch_forum_messages(
    client: TelegramClient,
    channel: Channel,
    start_date: datetime,
    end_date: datetime,
    my_username: str,
    limit=MAX_MESSAGES_PER_DIALOG
) -> Dict[str, List[Dict[str, str]]]:
    """Fetch messages from forum topics"""
    
    topics_result = {}
    
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    try:
        forum_topics = await client(GetForumTopicsRequest(
            channel=channel,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=limit
        ))
        
        topics_with_messages = 0
        
        for topic in forum_topics.topics[:limit]:
            if not hasattr(topic, 'title'):
                continue
                
            messages = []
            skipped_count = 0
            date_skipped = 0
            
            async for message in client.iter_messages(
                channel,
                limit=limit,
                reply_to=topic.id
            ):
                if not message.message:
                    skipped_count += 1
                    continue
                
                msg_date = message.date
                if not (start_date <= msg_date <= end_date):
                    date_skipped += 1
                    continue
                
                if message.sender:
                    sender_name = message.sender.username or message.sender.first_name
                    if sender_name == my_username:
                        skipped_count += 1
                        continue
                else:
                    sender_name = "Unknown"
                
                messages.append({
                    "name": sender_name,
                    "time": str(message.date),
                    "content": message.message
                })
            
            if messages:
                topics_result[topic.title] = messages
                topics_with_messages += 1
        
        return topics_result
        
    except Exception as e:
        return {}

async def fetch_messages(
    client: TelegramClient,
    dialog: Any,
    start_date: datetime,
    end_date: datetime,
    my_username: str
) -> List[Dict[str, str]]:
    """
    Fetches messages from a regular chat within a date range.
    
    Args:
        client: Telegram client instance
        dialog: Dialog to fetch messages from
        start_date: Start of date range
        end_date: End of date range
        my_username: Username to filter out own messages
        
    Returns:
        List of message dictionaries
    """
    messages = []
    
    # Ensure datetime objects are timezone-aware
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    
    try:
        async for message in client.iter_messages(dialog, limit=MAX_MESSAGES_PER_DIALOG):
            if not message.message:
                continue
                
            # Ensure message date is timezone-aware
            msg_date = message.date.replace(tzinfo=timezone.utc)
            if not (start_date <= msg_date <= end_date):
                continue
            
            # Improved sender name handling
            sender_name = "Channel Post"
            if message.sender:
                if message.sender.username:
                    sender_name = message.sender.username
                elif hasattr(message.sender, 'first_name'):
                    sender_name = message.sender.first_name
                    if hasattr(message.sender, 'last_name') and message.sender.last_name:
                        sender_name += f" {message.sender.last_name}"
                else:
                    sender_name = "Anonymous"
                    
            if sender_name == my_username:
                continue
                
            messages.append({
                "name": sender_name,
                "time": str(message.date),
                "content": message.message
            })
            
        return messages
        
    except Exception as e:
        #logger.error(f"Error fetching messages: {e}", exc_info=True)
        return []

async def process_dialog_messages(
    client: TelegramClient,
    dialog: Any,
    entity: Any,
    start_date: datetime,
    end_date: datetime,
    my_username: str
) -> Tuple[Optional[str], Any]:
    """
    Processes messages from a dialog based on its type.
    
    Args:
        client: Telegram client instance
        dialog: Dialog to process
        entity: Dialog entity
        start_date: Start of date range
        end_date: End of date range
        my_username: Username to filter out own messages
        
    Returns:
        Tuple of (chat_type, messages)
    """
    try:
        if hasattr(entity, 'forum') and entity.forum:
            return "group", await fetch_forum_messages(client, entity, start_date, end_date, my_username)
            
        elif hasattr(entity, 'megagroup') and entity.megagroup:
            #logger.debug(f"Processing supergroup: {dialog.name}")
            messages = await fetch_messages(client, dialog, start_date, end_date, my_username)
            return ("group", messages) if messages else (None, None)
            
        elif isinstance(entity, Channel):
            #logger.debug(f"Processing channel: {dialog.name}")
            messages = await fetch_messages(client, dialog, start_date, end_date, my_username)
            return ("channel", messages) if messages else (None, None)
            
        else:
            #logger.debug(f"Processing chat: {dialog.name}")
            messages = await fetch_messages(client, dialog, start_date, end_date, my_username)
            return ("chat", messages) if messages else (None, None)
            
    except Exception as e:
        #logger.error(f"Error processing dialog messages: {e}", exc_info=True)
        return None, None

async def process_dialogs(
    client: TelegramClient, 
) -> OrderedDict:
    """
    Process dialogs and return in LLM-friendly format.
    """
    start_date = datetime.now()
    end_date = datetime.now()
    output = {
        "metadata": {
            "date_range": {
                "start": str(start_date),
                "end": str(end_date)
            },
            "total_chats_processed": 0,
            "total_messages": 0,
            "collection_time": str(datetime.now()),
        },
        "conversations": []
    }
    
    all_messages = OrderedDict()
    processed_count = 0
    checked_count = 0
    
    my_username = await get_me(client)
    
    async for dialog in client.iter_dialogs():
        checked_count += 1
        
        if not is_valid_dialog(dialog):
            continue
            
        dialog_date = dialog.date
        if should_stop_processing(dialog, dialog_date, start_date, checked_count):
            break
            
        chat_type, messages = await process_dialog_messages(
            client, dialog, dialog.entity, start_date, end_date, my_username
        )
        
        if chat_type and messages:
            all_messages[dialog.name] = {
                "type": chat_type,
                "messages": messages
            }
            processed_count += 1
            
    
    for dialog_name, content in all_messages.items():
        chat_type = content["type"]
        messages = content["messages"]
        
        if isinstance(messages, dict):
            for topic, topic_messages in messages.items():
                processed_messages = []
                for msg in topic_messages:
                    message_dict = {
                        "name": msg["name"],
                        "content": msg["content"],
                        "timestamp": datetime.fromisoformat(msg["time"]).strftime("%Y-%m-%d %H:%M") if msg.get("time") else None
                    }
                    processed_messages.append(message_dict)
                
                processed_messages.sort(key=lambda x: x["timestamp"], reverse=False)

                output["conversations"].append({
                    "chat_name": dialog_name,
                    "type": chat_type,
                    "topic": topic,
                    "messages": processed_messages
                })
                output["metadata"]["total_messages"] += len(processed_messages)
        
        else:
            processed_messages = []
            for msg in messages:
                message_dict = {
                    "name": msg["name"],
                    "content": msg["content"],
                    "timestamp": datetime.fromisoformat(msg["time"]).strftime("%Y-%m-%d %H:%M") if msg.get("time") else None
                }
                processed_messages.append(message_dict)

            processed_messages.sort(key=lambda x: x["timestamp"], reverse=False)
            
            output["conversations"].append({
                "chat_name": dialog_name,
                "type": chat_type,
                "messages": processed_messages
            })
            output["metadata"]["total_messages"] += len(processed_messages)
            
    output["metadata"]["total_chats_processed"] = len(all_messages)
    
    return output 



async def get_me(client: TelegramClient) -> str:
    """Get the username of the authenticated user"""
    me = await client.get_me()
    username = me.username or me.first_name
    # logger.debug(f"Authenticated as user: {username}")
    return username 