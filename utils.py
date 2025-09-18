# in utils.py

import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Configure the Gemini API if the key is present
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    # Leave unconfigured; we'll handle gracefully in get_llm_response
    pass

# Use a single, consistent, current model name
MODEL_NAME = 'gemini-1.5-flash'
_gemini_model = None
try:
    if GEMINI_API_KEY:
        _gemini_model = genai.GenerativeModel(MODEL_NAME)
except Exception as _e:
    # Defer error reporting to runtime so the UI can show a friendly message
    _gemini_model = None


def _geocode_india(place_name: str):
    """Resolve a free-text place within India to lat/lon and a display name using OpenWeather Geocoding API.

    Returns a tuple: (latitude, longitude, resolved_name) or (None, None, None) if not found.
    """
    if not OPENWEATHER_API_KEY:
        return None, None, None
    if not place_name or not place_name.strip():
        return None, None, None

    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": f"{place_name},IN",
        "limit": 1,
        "appid": OPENWEATHER_API_KEY,
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        if isinstance(results, list) and results:
            first = results[0]
            lat = first.get("lat")
            lon = first.get("lon")
            name = first.get("name")
            state = first.get("state")
            country = first.get("country")
            display = ", ".join([p for p in [name, state, country] if p])
            return lat, lon, display
        return None, None, None
    except requests.exceptions.RequestException as _e:
        return None, None, None

def get_weather(place_name="Surat"):
    """Fetch current weather for an India place using geocoding + weather API.

    Returns a human-readable summary string including resolved place name and key metrics.
    """
    api_key = OPENWEATHER_API_KEY
    if not api_key:
        return "Weather API key is not set. Please configure OPENWEATHER_API_KEY."

    lat, lon, resolved = _geocode_india(place_name)
    if lat is None or lon is None:
        return f"Couldn't resolve location '{place_name}' in India. Please try a city or district name."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        rainfall = 0.0
        if isinstance(data.get('rain'), dict):
            rainfall = data['rain'].get('1h') or data['rain'].get('3h') or 0.0

        return (
            f"Weather in {resolved or place_name}: {temp}°C, {weather_description}, "
            f"humidity {humidity}%, wind {wind_speed} m/s, rainfall last hrs {rainfall} mm."
        )
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return "Sorry, I couldn't fetch the weather data right now."


def get_llm_response(user_message, weather_data):
    """Generates a response using the Gemini LLM."""
    if not GEMINI_API_KEY:
        return "Gemini API key is not set. Please configure GEMINI_API_KEY."
    if _gemini_model is None:
        return "LLM is not initialized. Please check your Gemini configuration."
    
    # Construct a detailed prompt
    prompt = f"""
    You are an expert agricultural assistant. Your task is to provide helpful advice to a farmer.
    
    Context:
    - Location & Current Weather (India-only): {weather_data}
    - Current Weather Data: {weather_data}
    
    Farmer's Question: "{user_message}"
    
    Based on the context and the farmer's question, provide a clear, concise, and actionable response.
    """
    
    try:
        response = _gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return "I'm having trouble connecting to my knowledge base. Please try again later."