import os
import tempfile

import numpy as np
import scipy.io.wavfile
import sounddevice as sd
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
CHANNELS = 1

# Start small. We can upgrade later.
WHISPER_MODEL = "base"


class TuesdaySTT:

    def __init__(self):

        print("Loading Faster-Whisper...")

        self.model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8",
        )

        print("Whisper ready.")

    def record(self, seconds=4):

        print()
        print("Listening for command...")
        print("Speak now.")

        audio = sd.rec(
            int(seconds * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
        )

        sd.wait()

        return audio[:, 0]

    def transcribe(self, audio):

        # Faster-Whisper works reliably with a WAV file.
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as f:

            temp_path = f.name

        try:

            scipy.io.wavfile.write(
                temp_path,
                SAMPLE_RATE,
                np.asarray(audio, dtype=np.int16),
            )

            segments, info = self.model.transcribe(
                temp_path,
                language="en",
                beam_size=5,
                vad_filter=True,
            )

            text = " ".join(
                segment.text.strip()
                for segment in segments
            ).strip()

            return text

        finally:

            if os.path.exists(temp_path):
                os.remove(temp_path)

    def listen(self, seconds=4):

        audio = self.record(seconds)

        print("Transcribing...")

        text = self.transcribe(audio)

        print()
        print("----------------------------------------")
        print("COMMAND:")
        print(text if text else "(nothing detected)")
        print("----------------------------------------")

        return text


if __name__ == "__main__":

    stt = TuesdaySTT()

    print()
    print("========================================")
    print(" Tuesday STT test")
    print("========================================")
    print("Speak a sentence.")
    print("Press Ctrl+C to exit.")

    try:

        while True:
            stt.listen()

    except KeyboardInterrupt:

        print()
        print("Stopped.")