import speech_recognition as sr

r = sr.Recognizer()

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
            return text.lower()
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

print("Speech-to-Text started. Speak 'exit' to stop.")
while True:
    text = record_text()
    if text == "exit":
        print("Exiting.")
        break
    if text:
        output_text(text)
print("Done. Check output.txt")

