# in app.py
import re
import chainlit as cl
import google.generativeai as genai
from utils import get_weather, get_llm_response # Import functions from your utils file

@cl.on_chat_start
async def start_chat():
    """
    This function runs when a new chat session starts.
    It sends a welcome message to the user.
    """
    await cl.Message(
        content="Hello! I am your agricultural assistant. Ask me anything about your crops or the weather.",
        author="AgriBot"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    This function is called every time a user sends a message.
    """
    # Show a loading indicator to the user
    msg = cl.Message(content="")
    await msg.send()
    
    # Try to extract a location mentioned by the user (e.g., "in/at/for/near Rajasthan")
    user_text = message.content or ""
    location = None
    match = re.search(r"\b(?:in|at|for|near)\s+([A-Za-z\s-]{2,})\b", user_text, flags=re.IGNORECASE)
    if match:
        location = match.group(1).strip()
    if not location:
        # Fallback default location
        location = "Surat"

    # Get the latest weather data for the extracted or default location
    weather_data = get_weather(location)
    
    # Get the LLM's response
    llm_response = get_llm_response(user_message=message.content, weather_data=weather_data)
    
    # Update the loading message with the final response
    msg.content = llm_response
    await msg.update()