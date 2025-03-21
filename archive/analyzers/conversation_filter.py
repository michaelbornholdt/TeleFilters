import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


def get_latest_messages_file(user_id: int) -> Tuple[Path, str]:
    """Get the path to the most recent messages file for a user and its timestamp"""
    messages_dir = Path("users") / str(user_id) / "messages"
    logger.info(f"Searching for messages in {messages_dir}")

    if not messages_dir.exists():
        raise FileNotFoundError(f"No messages directory found for user {user_id}")

    message_files = list(messages_dir.glob("messages_*.json"))
    if not message_files:
        raise FileNotFoundError(f"No message files found in {messages_dir}")

    # Sort files by modification time, newest first
    latest_file = max(message_files, key=lambda x: x.stat().st_mtime)
    # Extract timestamp from filename (e.g., "messages_2024-03-26_15-30.json")
    timestamp = latest_file.stem.replace("messages_", "")

    logger.info(f"Using latest messages file: {latest_file.name}")
    return latest_file, timestamp


"""Get the latest messages file for a user and its timestamp"""


class ConversationAnalyzer:
    def __init__(
        self,
        api_key,
        model,
        temperature,
        relevant_categories=None,
        irrelevant_topics=None,
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.categories = relevant_categories or []
        self.irrelevant = irrelevant_topics or []
        self.api_calls = 0
        logger.info(
            f"Initialized ConversationAnalyzer with model {model}, temperature {temperature}"
        )

    def _base_prompt(self):
        return """You are analyzing Telegram conversations from Berlin communities.

# Your Task:
Find relevant topics: Only focus on finding these!
- Events and meetups
- Requests for help or information

# Ignore these topics:
- Offers or sharing
- General announcements
- Introductions
- Flatshares
- Job offers

Please respond in this JSON format:
{
    "type": "event|request|offer|announcement",
    "summary": "Brief description of what's happening, Date and Location if mentioned and who is involved if relevant"
}

# Example output 
{
    "type": "request",
    "summary": "Kinky Market is happening on December 1st and volunteers are needed."
}
OR
{
    "type": "event",
    "summary": "Michael is inviting to a board game evening on the 12.12 starting at 18.00 at Standard Strasse 13a. React to the message to sign up." 
}
{
    "type": "event",
    "summary": "5th Birthday of the Burner Embassy Berlin is happening today (Saturday) at Haus der Statistik from 4pm-10pm. Activities include art, Burner Bingo, firespinning, and a potluck buffet. Location: Otto-Braun-Strasse 70, 10178 Berlin."
}

# Final Note

VERY IMPORTANT: Only respond if the conversation is relevant!
"""

    async def _call_llm(self, content: str) -> str:
        # Log the actual content being sent to LLM
        logger.debug(
            "\nInput to LLM:\n" + "-" * 40 + "\n" + content + "\n" + "-" * 40 + "\n"
        )

        messages = [
            {"role": "system", "content": self._base_prompt()},
            {"role": "user", "content": content},
        ]

        self.api_calls += 1  # Increment counter
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=500,
        )
        return completion.choices[0].message.content

    def _parse_llm_response(self, response: str) -> dict:
        """Parse the LLM response, handling both pure JSON and markdown-formatted JSON"""
        try:
            # Clean the response if it's wrapped in markdown code blocks
            cleaned_response = response
            if response.startswith("```json"):
                cleaned_response = (
                    response.replace("```json", "").replace("```", "").strip()
                )

            # Parse the cleaned JSON
            return json.loads(cleaned_response)

        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {response}")
            return {}  # Return empty dict on parse failure

    def _format_analysis_to_markdown(self, group: str, analysis: str) -> str:
        """Format a single analysis entry as markdown"""
        try:
            # Parse the JSON response from LLM using the new parser
            data = self._parse_llm_response(analysis)

            # Handle both single entry and array of entries
            if isinstance(data, list):
                entries = data
            else:
                entries = [data]

            # Format each entry
            markdown_entries = []
            for entry in entries:
                if entry.get("type") and entry.get("summary"):
                    markdown = f"**{group}**\n"
                    markdown += f"*{entry['type'].title()}*: {entry['summary']}"
                    if entry.get("details"):
                        markdown += f"\n_{entry['details']}_"
                    markdown_entries.append(markdown)

            return markdown_entries
        except Exception as e:
            logger.error(f"Failed to format analysis: {str(e)}")
            return []

    async def analyze_conversations(self, user_id: int, test_mode: bool = False):
        """Analyze conversations from the latest messages file and save results"""
        try:
            # Get latest file and its timestamp
            messages_file, timestamp = get_latest_messages_file(user_id)

            # Create analysis directory if it doesn't exist
            analysis_dir = Path("users") / str(user_id) / "analysis"
            analysis_dir.mkdir(exist_ok=True)

            # Load messages
            with open(messages_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Analyze messages
            markdown_entries = await self._analyze_data(data, test_mode)

            # Save results using same timestamp as input file
            output_file = analysis_dir / f"filtered_{timestamp}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(markdown_entries, f, ensure_ascii=False, indent=2)

            logger.info(f"Analysis complete. Results saved to {output_file}")
            return markdown_entries

        except Exception as e:
            logger.error(f"Error analyzing conversations: {e}")
            return []

    async def _analyze_data(self, data: dict, test_mode: bool) -> list:
        """Internal method to analyze the conversation data"""
        try:
            markdown_entries = []
            conversations = data.get("conversations", [])

            if test_mode:
                logger.info("Test mode: analyzing only first 3 conversations")
                conversations = conversations[:3]

            total = len(conversations)
            processed = 0

            for conversation in conversations:
                chat_name = conversation.get("chat_name", "Untitled")
                topic = conversation.get("topic", "")
                messages = conversation.get("messages", [])

                if not messages:
                    continue

                group_name = f"{chat_name}{' - Topic: ' + topic if topic else ''}"

                content = f"Channel: {chat_name}\n"
                if topic:
                    content += f"Topic: {topic}\n"
                content += "\nMessages:\n"

                for msg in messages:
                    name = msg.get("name", "Unknown")
                    text = msg.get("content", "")
                    timestamp = msg.get("timestamp", "")
                    weekday = datetime.fromisoformat(timestamp).strftime("%A")

                    # Format message with timestamp
                    if timestamp:
                        content += f"[{weekday} {timestamp}] {name}: {text}\n"
                    else:
                        content += f"{name}: {text}\n"

                try:
                    analysis = await self._call_llm(content)
                    processed += 1

                    entries = self._format_analysis_to_markdown(group_name, analysis)
                    markdown_entries.extend(entries)

                    logger.info(f"LLM Response for {chat_name}:\n{analysis}\n{'-'*80}")
                except Exception as e:
                    logger.error(f"Error analyzing {chat_name}: {str(e)}")

            logger.info(
                f"Analysis complete. Processed {processed} conversations with {self.api_calls} API calls."
            )
            return markdown_entries
        except Exception as e:
            logger.error(f"Error in _analyze_data: {e}")
            return []


# negative examples
"""
{
    "name": "ElinaCoLoving",
    "content": "Thank you all for another lovely temple on Friday, can’t wait to return next year! ☺️❤️ potentially our team can continue hosting while I’m away in winter🥰\nwe can pick up lost found 6pm-6:30pm at wamos tomorrow Monday",
    "timestamp": "2024-12-01 12:38"
}
{
    "name": "Krrisssk",
    "content": "I’m sorry for the flakiness but now this intense period of work is over and I plan to be more fresh once I’ve recovered haha:) let’s do something soon!",
    "timestamp": "2024-12-01 10:51"
}
"**Cohesion'24 - Bla Bla - Topic: General**\n*Request*: No relevant events or meetups found in the conversation.",
"**Berlin Burners (everything) - Topic: Buy/Sell/Gift/Request Stuff**\n*Request*: InvalidCharacter0 is looking to borrow motorcycle gear/clothes for a day.",
"**Berlin Burners (everything) - Topic: Flat search**\n*Offer*: Burcu is offering a bright and spacious 60m² 2-bedroom apartment in Kreuzberg/Neukölln for sublet during New Year's Eve from December 23 to January 7.",  
"""
