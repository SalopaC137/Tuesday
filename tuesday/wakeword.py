import os
import pickle
import time

import numpy as np
import sounddevice as sd
import openwakeword


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "tuesday_classifier.pkl",
)

SAMPLE_RATE = 16000
CHANNELS = 1

# Your training clips were 2 seconds / 32000 samples.
RECORD_SECONDS = 2.0

# Detection threshold.
THRESHOLD = 0.50

# Microphone device.
MIC_DEVICE = 1


class TuesdayWakeWord:

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

        print()
        print("========================================")
        print(" Tuesday wake detector")
        print("========================================")
        print(f"Microphone: {MIC_DEVICE}")
        print(f"Sample rate: {SAMPLE_RATE}")
        print(f"Window: {RECORD_SECONDS} seconds")
        print(f"Threshold: {THRESHOLD}")
        print()
        print("Say: Tuesday")
        print("Press Ctrl+C to exit.")
        print()

    def record_audio(self):

        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            device=MIC_DEVICE,
        )

        sd.wait()

        return audio[:, 0]

    def check_audio(self, audio):

        self.feature_extractor.reset()

        # IMPORTANT:
        # embed_clips() expects 16-bit PCM integers.
        audio = np.asarray(audio, dtype=np.int16)

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

    def listen(self):

        try:

            while True:

                print("Listening... say Tuesday.")

                audio = self.record_audio()

                probability = self.check_audio(audio)

                print(
                    f"Tuesday probability: {probability:.3f}"
                )

                if probability >= THRESHOLD:

                    print()
                    print(">>> TUESDAY DETECTED <<<")
                    print()

                    # Small pause prevents immediate
                    # duplicate detections.
                    time.sleep(0.5)

                else:

                    print("No detection.")
                    print()

        except KeyboardInterrupt:

            print()
            print("Stopped.")


if __name__ == "__main__":

    detector = TuesdayWakeWord()
    detector.listen()