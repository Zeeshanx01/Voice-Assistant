import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
import json
import wikipedia
import threading
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsApiKey = os.getenv("NEWS_API_KEY")
weatherApiKey = os.getenv("WEATHER_API_KEY")


# Speak Function using "pyttsx3 "
def speak_old(text):
    engine.say(text)
    engine.runAndWait()
    print("speak func run")


# Speak Function using "gTTS"
def speak(text):
    tts = gTTS(text)
    tts.save("temp.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    os.remove("temp.mp3")


# Function to send and recieve response from OpenAI
def get_weather(location):
    """Get weather information for a specific location"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={weatherApiKey}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            
            weather_info = f"The weather in {location} is {weather_desc}. "
            weather_info += f"The temperature is {temp}°C, feels like {feels_like}°C. "
            weather_info += f"The humidity is {humidity}%."
            
            return weather_info
        else:
            print(f"Error fetching weather: {response.status_code}")
            return None
    except Exception as e:
        print(f"Weather API error: {e}")
        return None


def search_wikipedia(query):
    """Search Wikipedia for information"""
    try:
        # Set language to English
        wikipedia.set_lang("en")
        
        # Get a summary of the topic (with 2 sentences)
        summary = wikipedia.summary(query, sentences=2)
        return f"According to Wikipedia: {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle disambiguation pages
        options = e.options[:5]  # Get first 5 options
        return f"There are multiple results for {query}. Some options are: {', '.join(options)}"
    except wikipedia.exceptions.PageError:
        return f"Sorry, I couldn't find any Wikipedia article about {query}."
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return f"Sorry, I encountered an error while searching for {query}."


def extract_time_from_command(command):
    """Extract time information from a command"""
    command = command.lower()
    time_str = ""
    
    # Check for minutes
    if "minute" in command or "minutes" in command:
        for word in command.split():
            if word.isdigit():
                time_str = f"{word} minutes"
                break
    
    # Check for hours
    elif "hour" in command or "hours" in command:
        for word in command.split():
            if word.isdigit():
                time_str = f"{word} hours"
                break
    
    # Check for seconds
    elif "second" in command or "seconds" in command:
        for word in command.split():
            if word.isdigit():
                time_str = f"{word} seconds"
                break
    
    return time_str


def set_timer(time_str):
    """Set a timer for the specified duration"""
    try:
        # Parse the time string
        duration = 0
        if "minute" in time_str or "minutes" in time_str:
            duration = int(time_str.split()[0]) * 60
        elif "hour" in time_str or "hours" in time_str:
            duration = int(time_str.split()[0]) * 3600
        elif "second" in time_str or "seconds" in time_str:
            duration = int(time_str.split()[0])
        else:
            # Try to interpret as just a number (assume seconds)
            try:
                duration = int(time_str)
            except ValueError:
                speak("I couldn't understand the time format. Please try again.")
                return
        
        # Confirm timer setting
        speak(f"Timer set for {time_str}.")
        
        # Start timer in a separate thread
        timer_thread = threading.Thread(target=run_timer, args=(duration,))
        timer_thread.daemon = True  # Thread will exit when main program exits
        timer_thread.start()
        
    except Exception as e:
        print(f"Error setting timer: {e}")
        speak("I encountered an error setting the timer.")


def run_timer(duration):
    """Run a timer for the specified duration in seconds"""
    try:
        time.sleep(duration)
        # Play alarm sound
        pygame.mixer.init()
        pygame.mixer.music.load("alarm.mp3")  # You need to have an alarm.mp3 file
        pygame.mixer.music.play()
        speak("Your timer has finished!")
        time.sleep(3)  # Let the alarm play for 3 seconds
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"Error in timer: {e}")


def set_reminder(message, time_str):
    """Set a reminder with a message for the specified time"""
    try:
        # Parse the time string
        duration = 0
        if "minute" in time_str or "minutes" in time_str:
            duration = int(time_str.split()[0]) * 60
        elif "hour" in time_str or "hours" in time_str:
            duration = int(time_str.split()[0]) * 3600
        elif "second" in time_str or "seconds" in time_str:
            duration = int(time_str.split()[0])
        else:
            # Try to interpret as just a number (assume seconds)
            try:
                duration = int(time_str)
            except ValueError:
                speak("I couldn't understand the time format. Please try again.")
                return
        
        # Calculate reminder time
        reminder_time = datetime.now() + timedelta(seconds=duration)
        formatted_time = reminder_time.strftime("%I:%M %p")
        
        # Confirm reminder setting
        speak(f"I'll remind you to {message} at {formatted_time}.")
        
        # Start reminder in a separate thread
        reminder_thread = threading.Thread(target=run_reminder, args=(duration, message))
        reminder_thread.daemon = True  # Thread will exit when main program exits
        reminder_thread.start()
        
    except Exception as e:
        print(f"Error setting reminder: {e}")
        speak("I encountered an error setting the reminder.")


def run_reminder(duration, message):
    """Run a reminder for the specified duration in seconds"""
    try:
        time.sleep(duration)
        # Play notification sound
        pygame.mixer.init()
        pygame.mixer.music.load("notification.mp3")  # You need to have a notification.mp3 file
        pygame.mixer.music.play()
        speak(f"Reminder: {message}")
        time.sleep(3)  # Let the notification play for 3 seconds
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"Error in reminder: {e}")


def aiProcess(command):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You're a virtual assistant named Jarvis, skilled in general tasks like Alexa and Google Cloud. Give short responses.",
            },
            {"role": "user", "content": command},
        ],
    )
    return completion.choices[0].message.content


def processCommand(c):
    print(c)
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open instagram" in c.lower():
        webbrowser.open("https://instagram.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open twitter" in c.lower():
        webbrowser.open("https://x.com")
    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)
    elif "news" in c.lower():
        r = requests.get(
            f"https://newsapi.org/v2/everything?q=Pakistan&apiKey={newsApiKey}"
        )
        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles", [])
            for article in articles[:3]:  # Limit to first 3 news items
                print(article["title"])
                speak(article["title"])
    elif "weather" in c.lower():
        # Extract location from command if provided, otherwise use default
        location = "London"  # Default location
        if "in" in c.lower():
            location = c.lower().split("in")[1].strip()
        
        weather_data = get_weather(location)
        if weather_data:
            speak(weather_data)
        else:
            speak("Sorry, I couldn't fetch the weather information at this time.")
    elif "wikipedia" in c.lower() or "search for" in c.lower():
        # Extract search query
        query = ""
        if "wikipedia" in c.lower():
            query = c.lower().replace("wikipedia", "").strip()
        elif "search for" in c.lower():
            query = c.lower().replace("search for", "").strip()
        
        if query:
            wiki_result = search_wikipedia(query)
            speak(wiki_result)
        else:
            speak("What would you like me to search for?")
            with sr.Microphone() as source:
                print("Listening for search query...")
                audio = r.listen(source)
                query = r.recognize_google(audio)
                wiki_result = search_wikipedia(query)
                speak(wiki_result)
    elif "timer" in c.lower() or "alarm" in c.lower() or "remind" in c.lower():
        # Extract time information
        if "set" in c.lower() and ("timer" in c.lower() or "alarm" in c.lower()):
            # Extract time duration
            time_str = extract_time_from_command(c)
            if time_str:
                set_timer(time_str)
            else:
                speak("For how long should I set the timer?")
                with sr.Microphone() as source:
                    print("Listening for timer duration...")
                    audio = r.listen(source)
                    time_str = r.recognize_google(audio)
                    set_timer(time_str)
        elif "remind" in c.lower():
            # Extract reminder message and time
            message = c.lower().replace("remind", "").replace("me", "").replace("to", "").strip()
            time_str = extract_time_from_command(c)
            if time_str:
                set_reminder(message, time_str)
            else:
                speak("When should I remind you?")
                with sr.Microphone() as source:
                    print("Listening for reminder time...")
                    audio = r.listen(source)
                    time_str = r.recognize_google(audio)
                    set_reminder(message, time_str)
    else:
        # OpenAI integration
        output = aiProcess(c)
        print(output)
        speak(output)


if __name__ == "__main__":
    speak("Initializing Jarvis...")
    while True:
        # Listen for the wake word "jarvis"
        # obtain audio from the microphone
        r = sr.Recognizer()
        # print("Recognizing")
        try:
            with sr.Microphone() as source:
                print("Speak Something...")
                speak("Speak Something...")
                audio = r.listen(source, timeout=2, phrase_time_limit=1)
            word = r.recognize_google(audio)
            print(f"USER: {word}")
            if word.lower() == "jarvis":
                print(f"JARVIS: Yes")
                speak(f"JARVIS: Yes")
                # Listen for command:
                with sr.Microphone() as source:
                    print("Jarvis Active... ")
                    speak("Jarvis Active... ")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)
                    processCommand(command)
        except Exception as e:
            err: str = "Error; {0}".format(e)
            print(err)
            speak(err)
