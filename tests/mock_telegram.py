from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from telethon.tl.types import Channel as TelegramChannel, User as TelegramUser
from telegram_bot.src.processors.message_processor import GetForumTopicsRequest  # Import from the main code

# Mock base classes that would normally come from telethon
class TelegramClient:
    pass

class Channel(TelegramChannel):
    def __init__(self, id: int, title: str):
        self.id = id
        self.title = title
        self._megagroup = False
        self._forum = False
        self.username = f"channel_{id}"

    @property
    def megagroup(self) -> bool:
        return self._megagroup

    @megagroup.setter
    def megagroup(self, value: bool):
        self._megagroup = value

    @property
    def forum(self) -> bool:
        return self._forum

    @forum.setter
    def forum(self, value: bool):
        self._forum = value

class User(TelegramUser):
    def __init__(self, id: int, username: str):
        super().__init__(
            id=id,
            is_self=False,
            contact=False,
            mutual_contact=False,
            deleted=False,
            bot=False,
            bot_chat_history=False,
            bot_nochats=False,
            verified=False,
            restricted=False,
            min=False,
            bot_inline_geo=False,
            support=False,
            scam=False,
            access_hash=0,
        )
        self.username = username
        self.first_name = "Test"
        self.last_name = "User"

@dataclass
class MockChannel(Channel):
    id: int
    title: str
    megagroup: bool = False
    forum: bool = False
    username: str = "test_channel"

@dataclass
class MockUser(User):
    id: int
    username: str
    first_name: str = "Test"
    last_name: str = "User"

@dataclass
class MockMessage:
    id: int
    text: str
    date: datetime
    sender: MockUser

class Dialog:
    def __init__(self, entity, folder_id=0):
        self.entity = entity
        self.folder_id = 0
        self.is_user = isinstance(entity, User)
        self.name = getattr(entity, 'title', None) or entity.username
        self.archived = False
        self.id = getattr(entity, 'id', 0)
        self.date = datetime.now()

class MockTopic:
    def __init__(self, id: int, title: str):
        self.id = id
        self.title = title

class MockTelegramClient:
    """Mock Telegram client with predefined test data"""
    
    def __init__(self):
        # Create the authenticated user (this is the bot/user running the client)
        self.me = User(id=999, username="my_bot_user")
        
        # Create other users for testing
        self.test_user = User(id=1, username="test_user")
        self.another_user = User(id=2, username="another_user")
        
        # Create mock channels/groups with explicit megagroup setting
        self.regular_group = Channel(id=100, title="Regular Group")
        self.regular_group.megagroup = True
        
        self.forum_group = Channel(id=101, title="Forum Group")
        self.forum_group.megagroup = True
        self.forum_group.forum = True
        
        self.channel = Channel(id=102, title="News Channel")
        
        # Create mock messages
        self.messages = {
            self.regular_group.id: [
                MockMessage(
                    id=1,
                    text="Hello from regular group",
                    date=datetime(2024, 3, 1, 12, 0),
                    sender=self.test_user  # Message from another user
                ),
                MockMessage(
                    id=2,
                    text="My message that should be filtered",
                    date=datetime(2024, 3, 1, 12, 30),
                    sender=self.me  # Message from the bot user
                ),
                MockMessage(
                    id=3,
                    text="Another user's message",
                    date=datetime(2024, 3, 1, 13, 0),
                    sender=self.another_user
                )
            ],
            self.forum_group.id: {
                "Topic 1": [
                    MockMessage(
                        id=4,
                        text="Forum topic 1 message",
                        date=datetime(2024, 3, 1, 13, 0),
                        sender=self.test_user
                    )
                ],
                "Topic 2": [
                    MockMessage(
                        id=5,
                        text="Forum topic 2 message",
                        date=datetime(2024, 3, 1, 14, 0),
                        sender=self.another_user
                    )
                ]
            },
            self.channel.id: [
                MockMessage(
                    id=6,
                    text="Channel announcement",
                    date=datetime(2024, 3, 1, 15, 0),
                    sender=self.test_user
                )
            ]
        }

    async def get_me(self):
        """Return the authenticated user"""
        return self.me

    async def iter_dialogs(self):
        """Simulate iterating through different chat types"""
        yield Dialog(self.regular_group, folder_id=0)
        yield Dialog(self.forum_group, folder_id=0)
        yield Dialog(self.channel, folder_id=0)
        yield Dialog(self.test_user, folder_id=1)

    async def iter_messages(self, dialog, limit=None, topic=None):
        """Simulate message iteration for a dialog"""
        dialog_id = getattr(dialog, 'id', None)
        messages = self.messages.get(dialog_id, [])
        
        if isinstance(messages, dict) and topic is not None:
            # Handle forum topics
            topic_messages = messages.get(f"Topic {topic + 1}", [])
            for msg in topic_messages[:limit]:
                yield msg
        elif isinstance(messages, list):
            # Handle regular messages
            for msg in messages[:limit]:
                yield msg

    async def __call__(self, request):
        """Handle forum topic requests"""
        print(f"Mock client received request: {type(request)}")
        if isinstance(request, GetForumTopicsRequest):
            print(f"Processing forum topics request")
            channel_id = request.peer.id
            if channel_id in self.messages and isinstance(self.messages[channel_id], dict):
                topics = [
                    MockTopic(id=idx, title=topic_name)
                    for idx, topic_name in enumerate(self.messages[channel_id].keys())
                ]
                return type('TopicsResponse', (), {'topics': topics})()
        return None 