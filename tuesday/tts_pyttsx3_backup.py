import pyttsx3


def speak(text):
    engine = pyttsx3.init()

    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    voices = engine.getProperty("voices")

    for voice in voices:
        name = (voice.name or "").lower()

        if "english" in name:
            engine.setProperty("voice", voice.id)
            print("Using voice:", voice.name)
            break

    print(f"Tuesday: {text}")

    engine.say(text)
    engine.runAndWait()

    engine.stop()


if __name__ == "__main__":

    print("========================================")
    print(" Tuesday TTS test")
    print("========================================")

    speak("Hello. I am Tuesday.")
    speak("My voice is working.")
    speak("What can I help you with?")