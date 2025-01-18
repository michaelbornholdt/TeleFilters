import pytest
from datetime import datetime
from collections import OrderedDict
from telegram_bot.src.processors.message_processor import process_dialogs, fetch_messages, fetch_topics_with_new_messages
from tests.mock_telegram import MockTelegramClient

@pytest.mark.asyncio
async def test_message_processing():
    """
    Test that we can correctly process messages from all types of chats
    """
    # Setup
    client = MockTelegramClient()
    end_date = datetime(2024, 3, 2)
    start_date = datetime(2024, 3, 1)
    
    result = await process_dialogs(client, start_date, end_date)
    
    # Debug print
    print("\nResult contents:")
    for name, data in result.items():
        print(f"{name}: {data}")

    # Verify structure and content
    assert isinstance(result, OrderedDict)
    
    # Check Regular Group
    assert "Regular Group" in result, "Regular Group not found in results"
    regular_group = result["Regular Group"]
    assert regular_group is not None, "Regular Group data is None"
    assert "type" in regular_group, f"No 'type' in regular_group data: {regular_group}"
    assert regular_group["type"] == "group", f"Expected type 'group', got {regular_group.get('type')}"
    assert isinstance(regular_group["messages"], list), "Regular group messages should be a list"
    
    # Check Forum Group
    assert "Forum Group" in result
    forum_group = result["Forum Group"]
    assert forum_group["type"] == "group"
    assert isinstance(forum_group["messages"], dict), "Forum group messages should be a dictionary"
    
    # Check forum topics
    assert "Topic 1" in forum_group["messages"], "Topic 1 not found in forum messages"
    assert "Topic 2" in forum_group["messages"], "Topic 2 not found in forum messages"
    
    # Check topic messages
    topic1_messages = forum_group["messages"]["Topic 1"]
    assert isinstance(topic1_messages, list), "Topic messages should be a list"
    assert len(topic1_messages) > 0, "Topic 1 should have messages"
    assert topic1_messages[0]["name"] == "test_user"
    assert "Forum topic 1 message" in topic1_messages[0]["content"]
    
    # Check Channel
    assert "News Channel" in result
    news_channel = result["News Channel"]
    assert news_channel["type"] == "channel"
    assert isinstance(news_channel["messages"], list), "Channel messages should be a list"

    print("\nTest Results:")
    for chat_name, chat_data in result.items():
        print(f"\n{chat_name} ({chat_data['type']}):")
        if chat_data['type'] == "group" and isinstance(chat_data["messages"], dict):
            # Handle forum group messages
            for topic_name, topic_messages in chat_data["messages"].items():
                print(f"  Topic: {topic_name}")
                for msg in topic_messages:
                    print(f"    {msg['name']}: {msg['content']}")
        else:
            # Handle regular group and channel messages
            if isinstance(chat_data["messages"], list):
                for msg in chat_data["messages"]:
                    print(f"  {msg['name']}: {msg['content']}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 