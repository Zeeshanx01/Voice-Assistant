import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
from dotenv import load_dotenv

recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsApiKey = os.getenv("NEWS_API_KEY")

# Load variables from .env
load_dotenv()


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
    elif "news" in c.lower:
        r = requests.get(
            f"https://newsapi.org/v2/everything?q=Pakistan&apiKey={newsApiKey}"
        )
        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles", [])
            for article in articles:
                print(article["title"])
                speak(article["title"])
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
