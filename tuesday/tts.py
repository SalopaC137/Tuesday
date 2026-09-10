import os
import tempfile
import wave

import winsound
from piper import PiperVoice


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

VOICE_MODEL = os.path.join(
    BASE_DIR,
    "en_US-amy-medium.onnx",
)


# ============================================================
# LOAD AMY ONCE
# ============================================================

print("Loading Amy voice...")

voice = PiperVoice.load(
    VOICE_MODEL
)

print("Amy voice ready.")


# ============================================================
# SPEAK
# ============================================================

def speak(text):

    if not text:
        return

    print(
        f"Tuesday: {text}"
    )

    temp_wav = os.path.join(
        tempfile.gettempdir(),
        "tuesday_speech.wav",
    )

    try:

        # Generate speech using the
        # already-loaded Amy model.
        with wave.open(
            temp_wav,
            "wb",
        ) as wav_file:

            voice.synthesize_wav(
                text,
                wav_file,
            )

        # Play immediately.
        winsound.PlaySound(
            temp_wav,
            winsound.SND_FILENAME,
        )

    except Exception as e:

        print(
            "TTS error:",
            e
        )

    finally:

        try:

            if os.path.exists(temp_wav):
                os.remove(temp_wav)

        except OSError:
            pass


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )
    print(
        " Tuesday Amy TTS test"
    )
    print(
        "========================================"
    )

    speak(
        "Hello. I am Tuesday."
    )

    speak(
        "My voice is powered by Amy."
    )

    speak(
        "I am ready to help you."
    )