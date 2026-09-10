import os
import pickle
import time

import numpy as np
import scipy.io.wavfile
import sounddevice as sd
from faster_whisper import WhisperModel
import openwakeword

from commands import TuesdayCommands
from tts import speak
from ai import TuesdayAI


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "tuesday_classifier.pkl",
)

MIC_DEVICE = 1

SAMPLE_RATE = 16000
CHANNELS = 1

# Wake-word detection window.
# Keep this at the length that worked in your previous detector.
WAKE_SECONDS = 2

# Command recording length.
COMMAND_SECONDS = 6

COMMAND_BLOCK = 0.1
COMMAND_START_RMS = 250
COMMAND_SILENCE_RMS = 120
COMMAND_END_SILENCE = 0.8
COMMAND_MAX_SILENCE = 8.0

WAKE_THRESHOLD = 0.55

WHISPER_MODEL = "small"
CONVERSATION_TIMEOUT = 8.0


# ============================================================
# TUESDAY ASSISTANT
# ============================================================

class TuesdayAssistant:

    def __init__(self):

        print("Loading Tuesday classifier...")

        with open(MODEL_PATH, "rb") as f:
            self.classifier = pickle.load(f)

        print("Loading audio feature extractor...")

        self.oww = openwakeword.Model(
            wakeword_models=["hey_jarvis"],
            inference_framework="onnx",
        )

        self.feature_extractor = self.oww.preprocessor

        print("Loading Whisper...")

        self.whisper = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8",
        )

        self.commands = TuesdayCommands()
        self.ai = TuesdayAI()

    # --------------------------------------------------------
    # RECORD AUDIO
    # --------------------------------------------------------

    def record(self, seconds):

        audio = sd.rec(
            int(seconds * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            device=MIC_DEVICE,
        )

        sd.wait()

        return audio[:, 0]

    # --------------------------------------------------------
    # WAKE WORD
    # --------------------------------------------------------

    def check_wake_word(self, audio):

        self.feature_extractor.reset()

        embeddings = self.feature_extractor.embed_clips(
            audio[np.newaxis, :],
            batch_size=1,
            ncpu=1,
        )

        features = embeddings.reshape(
            embeddings.shape[0],
            -1,
        )

        probability = self.classifier.predict_proba(
            features
        )[0, 1]

        return float(probability)

    # --------------------------------------------------------
    # COMMAND
    # --------------------------------------------------------

    def listen_for_command(self):

        print("Listening for command...")
        print("Speak now.")

        time.sleep(0.25)

        block_samples = int(
            COMMAND_BLOCK * SAMPLE_RATE
        )

        blocks = []

        speech_started = False
        silence_time = 0.0

        start_wait_time = 0.0

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            device=MIC_DEVICE,
            blocksize=block_samples,
        ) as stream:

            while True:

                audio_block, overflowed = stream.read(
                    block_samples
                )

                audio_block = audio_block[:, 0].copy()

                rms = np.sqrt(
                    np.mean(
                        audio_block.astype(
                            np.float32
                        ) ** 2
                    )
                )

                if not speech_started:

                    start_wait_time += COMMAND_BLOCK

                    if rms >= COMMAND_START_RMS:

                        speech_started = True

                        print("Speech detected.")

                        blocks.append(audio_block)

                    elif start_wait_time >= COMMAND_MAX_SILENCE:

                        print("No command detected.")

                        return ""

                else:

                    blocks.append(audio_block)

                    if rms < COMMAND_SILENCE_RMS:

                        silence_time += COMMAND_BLOCK

                    else:

                        silence_time = 0.0

                    if silence_time >= COMMAND_END_SILENCE:

                        print("Speech finished.")

                        break

                    if len(blocks) * COMMAND_BLOCK >= COMMAND_SECONDS:

                        print("Maximum command length reached.")

                        break

        audio = np.concatenate(blocks)

        temp_path = os.path.join(
            BASE_DIR,
            "_command.wav",
        )

        scipy.io.wavfile.write(
            temp_path,
            SAMPLE_RATE,
            audio,
        )

        print("Transcribing...")

        try:

            segments, info = self.whisper.transcribe(
                temp_path,
                language="en",
                task="transcribe",
                beam_size=5,
                temperature=0,
                condition_on_previous_text=False,
                vad_filter=True,
            )

            text = " ".join(
                segment.text.strip()
                for segment in segments
            ).strip()

        finally:

            try:
                os.remove(temp_path)
            except OSError:
                pass

        return text
    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------
    def conversation_loop(self):

        print()
        print("Conversation mode active.")
        print("Speak another command, or stay silent to sleep.")

        last_activity = time.time()

        while True:

            # ------------------------------------------------
            # Wait for another command.
            # ------------------------------------------------

            print()
            print("Listening for follow-up...")

            start_time = time.time()

            command = self.listen_for_command()

            # ------------------------------------------------
            # Nothing heard.
            # ------------------------------------------------

            if not command:

                elapsed = time.time() - start_time

                if elapsed >= CONVERSATION_TIMEOUT:

                    print("Conversation timeout.")
                    print("Returning to wake-word mode.")

                    return

                continue

            # ------------------------------------------------
            # Display command.
            # ------------------------------------------------

            print()
            print("----------------------------------------")
            print("COMMAND:")
            print(command)
            print("----------------------------------------")

            # ------------------------------------------------
            # Local command router.
            # ------------------------------------------------

            response = self.commands.handle(command)

            # ------------------------------------------------
            # STOP.
            # ------------------------------------------------

            if response == "__STOP__":

                speak("Going to sleep.")

                print("Tuesday going to sleep.")

                return

            # ------------------------------------------------
            # AI fallback.
            # ------------------------------------------------

            if response is None:

                print("Tuesday AI: Thinking...")

                response = self.ai.ask(command)

                print()
                print("----------------------------------------")
                print("TUESDAY:")
                print(response)
                print("----------------------------------------")

            # ------------------------------------------------
            # Speak response.
            # ------------------------------------------------

            speak(response)

            last_activity = time.time()
    def run(self):

        print()
        print("========================================")
        print("        TUESDAY ASSISTANT")
        print("========================================")
        print("Say 'Tuesday' to wake me.")
        print("Say 'Tuesday, stop' to stop.")
        print("Press Ctrl+C to exit.")
        print()

        while True:

            try:

                # --------------------------------------------
                # WAIT FOR WAKE WORD
                # --------------------------------------------

                audio = self.record(WAKE_SECONDS)

                probability = self.check_wake_word(audio)

                print(
                    f"\rTuesday probability: {probability:.3f}",
                    end="",
                    flush=True,
                )

                if probability < WAKE_THRESHOLD:
                    continue

                print()
                print()
                print(">>> TUESDAY DETECTED <<<")

                # --------------------------------------------
                # ACKNOWLEDGE
                # --------------------------------------------

                speak("Yes?")

                # --------------------------------------------
                # LISTEN FOR COMMAND
                # --------------------------------------------

                command = self.listen_for_command()

                if not command:

                    print("No command detected.")
                    continue

                print()
                print("----------------------------------------")
                print("COMMAND:")
                print(command)
                print("----------------------------------------")

                # --------------------------------------------
                # COMMAND ROUTER
                # --------------------------------------------

                response = self.commands.handle(command)

                if response == "__STOP__":

                    speak("Going to sleep.")

                    print()
                    print("Tuesday stopped.")

                    break

                if response is None:

                    print("Tuesday AI: Thinking...")

                    response = self.ai.ask(command)

                    print()
                    print("----------------------------------------")
                    print("TUESDAY:")
                    print(response)
                    print("----------------------------------------")

                speak(response)

                # --------------------------------------------
                # ENTER CONVERSATION MODE
                # --------------------------------------------

                self.conversation_loop()

                print()
                print("Listening for Tuesday...")

                time.sleep(0.2)

            except KeyboardInterrupt:

                print()
                print()
                print("Tuesday stopped.")
                break


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    assistant = TuesdayAssistant()
    assistant.run()