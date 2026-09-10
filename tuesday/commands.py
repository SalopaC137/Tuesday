import datetime
import re
from media import TuesdayMedia
from apps import TuesdayApps


class TuesdayCommands:

    def __init__(self):

        self.name = "Tuesday"
        self.apps = TuesdayApps()

        # Local media controller
        self.media = TuesdayMedia()

    # ========================================================
    # COMMAND HANDLER
    # ========================================================

    def handle(self, text):

        text = text.lower().strip()

        # Remove punctuation so:
        # "play music!" -> "play music"
        # "play memories." -> "play memories"
        text = re.sub(r"[^\w\s]", "", text)
        text = " ".join(text.split())

        if not text:
            return "I didn't hear a command."

        # ====================================================
        # STOP TUESDAY
        # ====================================================

        if any(phrase in text for phrase in [
            "go to sleep",
            "shut down",
            "goodbye",
            "tuesday stop",
        ]):

            return "__STOP__"

        # ====================================================
        # MUSIC / MEDIA STOP
        # ====================================================

        if any(phrase in text for phrase in [
            "stop the music",
            "stop music",
            "stop the song",
            "stop playing",
            "stop playback",
            "stop the video",
            "stop video",
        ]):

            return self.media.stop()

        # ====================================================
        # PAUSE
        # ====================================================

        if any(phrase in text for phrase in [
            "pause",
            "pause the music",
            "pause music",
            "pause the song",
            "pause playback",
            "pause the video",
            "pause video",
        ]):

            return self.media.pause()

        # ====================================================
        # RESUME
        # ====================================================

        if any(phrase in text for phrase in [
            "resume",
            "resume music",
            "resume the music",
            "resume song",
            "resume video",
            "continue",
            "continue playing",
            "continue the music",
            "continue the video",
        ]):

            return self.media.resume()

        # ====================================================
        # NEXT
        # ====================================================

        if any(phrase in text for phrase in [
            "next",
            "next song",
            "next track",
            "next one",
            "skip",
            "skip song",
            "skip this song",
            "play next",
            "play the next song",
        ]):

            return self.media.next_track()

        # ====================================================
        # PREVIOUS
        # ====================================================

        if any(phrase in text for phrase in [
            "previous",
            "previous song",
            "previous track",
            "go back",
            "play that again",
            "play it again",
            "repeat that",
            "repeat the song",
            "go back to the last song",
            "play previous",
        ]):

            return self.media.previous_track()

        # ====================================================
        # VOLUME UP
        # ====================================================

        if any(phrase in text for phrase in [
            "volume up",
            "turn it up",
            "i cant hear",
            "i can't hear",
            "turn the volume up",
            "increase volume",
            "louder",
        ]):

            return self.media.volume_up()

        # ====================================================
        # VOLUME DOWN
        # ====================================================

        if any(phrase in text for phrase in [
            "volume down",
            "turn it down",
            "its too loud",
            "it's too loud",
            "turn the volume down",
            "decrease volume",
            "quieter",
        ]):

            return self.media.volume_down()

        # ====================================================
        # PLAY VIDEO
        # ====================================================

        if text.startswith("play video "):

            query = text[
                len("play video "):
            ].strip()

            if not query:

                return self.media.play_random_video()

            results = self.media.search(
                query,
                media_type="video",
            )

            if not results:

                return (
                    f"I couldn't find a video "
                    f"matching {query}."
                )

            # Use the media controller's file playback.
            item = results[0]

            if not self.media.play_file(item):

                return (
                    "I couldn't start the video."
                )

            # Video playback doesn't currently have
            # a search/genre next mode.
            self.media.play_mode = "search"
            self.media.play_query = query

            return (
                f"Playing {item['name']}."
            )

        # ====================================================
        # RANDOM VIDEO
        # ====================================================

        if text in [
            "play a video",
            "play video",
            "play me a video",
            "play some video",
            "play a random video",
        ]:

            return self.media.play_random_video()

        # ====================================================
        # PLAY MUSIC
        # ====================================================

        if text.startswith("play "):

            query = text[
                len("play "):
            ].strip()

            # ------------------------------------------------
            # No query
            # ------------------------------------------------

            if not query:

                return self.media.play_random()

            # ------------------------------------------------
            # RANDOM MUSIC
            # ------------------------------------------------

            if query in [
                "music",
                "some music",
                "a song",
                "some songs",
                "something",
                "something random",
                "random music",
                "random song",
            ]:

                return self.media.play_random()

            # ------------------------------------------------
            # NORMAL SEARCH
            # ------------------------------------------------

            return self.media.play(query)

        # ====================================================
        # TIME
        # ====================================================

        if (
            "what time" in text
            or "what is the time" in text
            or "what's the time" in text
            or "tell me the time" in text
            or "current time" in text
            or "time right now" in text
            or text == "time is it"
        ):

            now = datetime.datetime.now()

            return now.strftime(
                "It is %I:%M %p."
            ).replace(" 0", " ")

        # ====================================================
        # DAY
        # ====================================================

        if (
            "what day" in text
            or "what is the day" in text
            or "what's the day" in text
            or "day today" in text
            or "what day is today" in text
            or "tell me the day" in text
        ):

            today = datetime.datetime.now()

            return today.strftime(
                "Today is %A."
            )

        # ====================================================
        # DATE
        # ====================================================

        if (
            "what date" in text
            or "what is the date" in text
            or "what's the date" in text
            or "date today" in text
            or "today's date" in text
            or "today date" in text
            or "tell me the date" in text
        ):

            today = datetime.datetime.now()

            return today.strftime(
                "Today is %A, %B %d, %Y."
            )

        # ====================================================
        # NAME
        # ====================================================

        if (
            "your name" in text
            or "who are you" in text
            or "what are you" in text
        ):

            return (
                "I'm Tuesday, your voice assistant."
            )

        # ====================================================
        # HOW ARE YOU
        # ====================================================

        if (
            "how are you" in text
            or "how are you doing" in text
        ):

            return (
                "I'm doing great. Thanks for asking."
            )

        # ====================================================
        # GREETINGS
        # ====================================================

        if any(phrase in text for phrase in [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        ]):

            return "Hello. How can I help?"

        # ====================================================
        # UNKNOWN
        # ====================================================

        return None


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    router = TuesdayCommands()

    print()
    print("========================================")
    print(" Tuesday command router test")
    print("========================================")
    print("Type commands below.")
    print("Press Ctrl+C to exit.")

    try:

        while True:

            text = input("\nCommand: ")

            response = router.handle(text)

            if response == "__STOP__":

                print(
                    "Tuesday going to sleep."
                )

                break

            if response is None:

                print(
                    "UNKNOWN COMMAND"
                )

            else:

                print(
                    "Tuesday:",
                    response
                )

    except KeyboardInterrupt:

        print()
        print("Stopped.")