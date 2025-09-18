# in utils.py

import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.0-pro') 

def get_weather(city_name="Surat"):
    """Fetches weather data from OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"  # For Celsius
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise an error for bad responses (4xx or 5xx)
        data = response.json()
        
        # Format the weather data into a readable string
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        return f"The current weather in {city_name} is {temp}°C with {weather_description}, {humidity}% humidity, and a wind speed of {wind_speed} m/s."

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return "Sorry, I couldn't fetch the weather data right now."


def get_llm_response(user_message, weather_data):
    """Generates a response using the Gemini LLM."""
    model = genai.GenerativeModel('gemini-pro')
    
    # Construct a detailed prompt
    prompt = f"""
    You are an expert agricultural assistant. Your task is to provide helpful advice to a farmer.
    
    Context:
    - The farmer is located near Surat, Gujarat, India.
    - Current Weather Data: {weather_data}
    
    Farmer's Question: "{user_message}"
    
    Based on the context and the farmer's question, provide a clear, concise, and actionable response.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return "I'm having trouble connecting to my knowledge base. Please try again later."