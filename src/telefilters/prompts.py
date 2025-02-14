import asyncio
import logging
import os
import typing as t
from datetime import datetime

from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

SYSTEM_PROMPT = """
    You are a Berliner, who knows very well the public transport system.
    You are helping the user playing the game of avoiding getting controled by the ticket inspectors."
    First, figure out which lines the user is taking (S, U, M, etc.) and the stations they are passing through.
    Then, figure out which stations on the way intersect with any other lines. \n\n
    You will also receive the hints of the locations of the ticket inspectors and give user the assessement of the
    risk of getting controled on the specified journey. Provide also the reasoning behind your assessment. Reason should be
    based on the recent locations of the controllers and how that relates to the user's journey.
    """


SUMMARY_PROMPT = """
    Based on the provided analysis, give a brief, direct response about:
    1. The overall risk level (Low/Medium/High)
    2. Key reasons for your assessment, they should directly reflect recent
    sightings of ticket inspectors with times and locations information.
    Keep your response under 5 sentences and be direct.
    """


async def get_freifahren_risk_assessment(
    client: OpenAI,
    user_prompt: str,
    freifahren_prompt: str,
    system_prompt: t.Optional[str] = None,
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
    max_tokens: t.Optional[int] = None,
) -> str:
    """Get a risk assessment for encountering ticket inspectors.

    Makes two API calls:
    1. Detailed analysis of the situation
    2. Concise summary for the user

    Args:
        client: OpenAI client
        user_prompt: User's journey question
        freifahren_prompt: Recent inspector sightings
        system_prompt: Optional override for system prompt
        model: OpenAI model to use
        temperature: Response randomness (0.0-2.0)
        max_tokens: Maximum tokens in response

    Returns:
        str: Concise risk assessment message
    """
    time = datetime.now().strftime("%H:%M")

    context_prompt = f"""
    Here are the hints of the locations of the ticket inspectors. They are based on the recent reports from the community.
    Each message consists of time in H:M format and a text from community. Text can be either in german or english. Current time is {time}.
    \nHere are the last 20 messages:\n
    {freifahren_prompt}
    """

    try:
        # First call: Detailed analysis
        detailed_analysis = await _make_openai_call(
            client=client,
            system_prompt=SYSTEM_PROMPT,
            user_prompts=[context_prompt, user_prompt],
            model=model,
            temperature=temperature,
            max_tokens=1000,  # Allow longer response for analysis
        )

        logger.info(f"Detailed analysis:\n{detailed_analysis}")

        # Second call: Concise summary
        summary_prompt = f"Based on this analysis:\n{detailed_analysis}\n\nProvide a concise risk assessment."
        final_response = await _make_openai_call(
            client=client,
            system_prompt=SUMMARY_PROMPT,
            user_prompts=[summary_prompt],
            model=model,
            temperature=temperature,
            max_tokens=150,  # Keep summary brief
        )

        logger.info(f"Final response:\n{final_response}")
        return final_response

    except Exception as e:
        logger.error(f"Error getting risk assessment: {str(e)}")
        raise


async def _make_openai_call(
    client: OpenAI,
    system_prompt: str,
    user_prompts: t.List[str],
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """Helper function to make OpenAI API calls.

    Args:
        client: OpenAI client
        system_prompt: System message
        user_prompts: List of user messages
        model: OpenAI model
        temperature: Response randomness
        max_tokens: Maximum tokens

    Returns:
        str: Assistant's response
    """
    try:
        loop = asyncio.get_event_loop()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(
            [{"role": "user", "content": prompt} for prompt in user_prompts]
        )

        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ),
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error in OpenAI call: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    import os

    # Get authenticated client using your existing function
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    user_prompt = "going from U5 samariterstr to U8 voltastr"

    messages = [
        ("13:54", "Whats happened with S bahn?"),
        ("14:08", "something fire related apparently"),
        ("14:16", "Which stations are affected or suspended?"),
        (
            "14:18",
            "i was at schöneweide when they said the delays are due to fire brigade activity. now i'm onnth 9 and it seems this line is back on schedule",
        ),
        ("14:19", "no idea about other lines"),
        ("14:20", "t the"),
        ("14:27", "u9 westhafen mit blauer weste gerade ausgestiegen"),
        ("14:33", "S41 Hermanstraße eingestiegen 2 Zivis"),
        ("14:57", "Blauwesten u Turmstraße  Richtung Steglitz mittig"),
        (
            "15:04",
            "Gleiche Spiel am Zoo zwei weibliche blauwesten mittig auf u 9 gleis",
        ),
        ("15:21", "Hansaplatz"),
        ("16:04", "2 blaue Westen U7 Richtung Rudow, Wutzkyallee"),
        ("16:10", "Friedrichstraße, drei Personen eine Frau und zwei Typen"),
        ("16:50", "U9 Leopoldplatz mit Westen"),
        (
            "17:29",
            "Über app.freifahren.org gab es folgende Meldung:\n\n**Station**: Alt-Moabit\n**Line**: M10",
        ),
        ("17:55", "S46 Richtung Tempelhof an der Hermannstraße"),
        ("18:29", "At Tempelhof getting in s41 to sudkreuz"),
        (
            "18:42",
            "Über app.freifahren.org gab es folgende Meldung:\n\n**Station**: Gesundbrunnen\n**Line**: U8\n**Beschreibung**: 3x cops standing on the line towards hermannstr.",
        ),
        ("20:04", "Only Security"),
        (
            "20:08",
            "Big control at ostkreuz at the entrance to the station where the escalator is off of noldnerstrasse, I don't know what they are doing but they seem to be stopping people before entering even",
        ),
    ]
    prompt_freifahren = "\n".join([f"{time}: {text}" for time, text in messages])

    try:
        response = get_freifahren_risk_assessment(
            client=openai_client,
            user_prompt=user_prompt,
            freifahren_prompt=prompt_freifahren,
        )
        print(f"Assistant's response:\n{response}")

    except Exception as e:
        print(f"Failed to get response: {str(e)}")
