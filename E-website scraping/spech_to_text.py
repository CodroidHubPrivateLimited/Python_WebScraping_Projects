import os

import requests
import speech_recognition as sr

r = sr.Recognizer()
VOICE_SERVER_URL = os.getenv("VOICE_SERVER_URL", "http://localhost:5000/voice-command")

def record_text():
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Speak now!")
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Recognizing...")
            text = r.recognize_google(audio)
            print("Recognized:", text)
            return text
    except sr.WaitTimeoutError:
        print("No speech (timeout)")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None

def output_text(text):
    if text:
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"Wrote to output.txt: {text}")


def send_to_ui(text):
    if not text:
        return
    try:
        response = requests.post(
            VOICE_SERVER_URL,
            json={"text": text},
            timeout=2,
        )
        if response.status_code != 200:
            print(f"Voice bridge error: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Voice bridge error: {e}")

print("Speech-to-Text started. Speak 'exit' to stop.")
while True:
    text = record_text()
    if text and text.lower() == "exit":
        print("Exiting.")
        break
    if text:
        output_text(text)
        send_to_ui(text)
print("Done. Check output.txt")

