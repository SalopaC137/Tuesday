import os
import random
import socket
import subprocess
import time
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

MUSIC_ROOT = Path(r"D:\Music")
MOVIE_ROOT = Path(r"D:\Movies")

VLC_PATH = Path(
    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
)

AUDIO_EXTENSIONS = {
    ".mp3",
    ".m4a",
    ".aac",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
}
MOVIE_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
}
VLC_HOST = "127.0.0.1"
VLC_PORT = 4212


# ============================================================
# TUESDAY MEDIA CONTROLLER
# ============================================================

class TuesdayMedia:

    def __init__(self):

        self.music_root = MUSIC_ROOT

        self.library = []

        self.vlc_process = None
        self.vlc_socket = None

        self.current_item = None
        self.paused = False

        # ----------------------------------------------------
        # Playback context
        # ----------------------------------------------------

        # random
        # genre
        # search
        self.play_mode = None

        # Query associated with the current mode.
        #
        # Examples:
        #   "pop"
        #   "gospel"
        #   "drake"
        #
        self.play_query = None

        # ----------------------------------------------------
        # Playback history
        # ----------------------------------------------------

        self.last_items = []

        # Maximum history size.
        self.history_limit = 50

        print("Loading local music library...")

        self.scan_library()

        print(
            f"Found {len(self.library)} media files."
        )

    # ========================================================
    # SCAN LIBRARY
    # ========================================================

    def scan_library(self):

        if not self.music_root.exists():

            print(
                f"WARNING: Music folder not found: "
                f"{self.music_root}"
            )

            return

        for path in self.music_root.rglob("*"):

            if not path.is_file():
                continue

            extension = path.suffix.lower()

            if extension not in (
                AUDIO_EXTENSIONS
                | VIDEO_EXTENSIONS
            ):
                continue

            relative = path.relative_to(
                self.music_root
            )

            parts = relative.parts

            media_type = (
                "video"
                if extension in VIDEO_EXTENSIONS
                else "audio"
            )

            # ------------------------------------------------
            # Genre
            # ------------------------------------------------

            genre = ""

            if len(parts) >= 2:

                genre = parts[-2].lower()

            self.library.append({

                "path": path,

                "name": path.stem,

                "type": media_type,

                "genre": genre,

            })

    # ========================================================
    # START VLC
    # ========================================================

    def start_vlc(self):

        if self.vlc_process is not None:

            if self.vlc_process.poll() is None:

                return True

        if not VLC_PATH.exists():

            print(
                f"ERROR: VLC not found: {VLC_PATH}"
            )

            return False

        print(
            "Starting Tuesday's VLC player..."
        )

        self.vlc_process = subprocess.Popen(

            [
                str(VLC_PATH),

                "--extraintf",
                "rc",

                "--rc-host",
                f"{VLC_HOST}:{VLC_PORT}",

                "--no-video-title-show",
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL,
        )

        # Give VLC time to open
        # the RC interface.

        for _ in range(20):

            if self.connect_vlc():

                return True

            time.sleep(0.1)

        print(
            "ERROR: Could not connect to VLC."
        )

        return False

    # ========================================================
    # CONNECT TO VLC
    # ========================================================

    def connect_vlc(self):

        if self.vlc_socket is not None:

            try:

                self.vlc_socket.close()

            except Exception:

                pass

            self.vlc_socket = None

        try:

            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
            )

            sock.settimeout(1)

            sock.connect(
                (
                    VLC_HOST,
                    VLC_PORT,
                )
            )

            self.vlc_socket = sock

            try:

                sock.recv(4096)

            except socket.timeout:

                pass

            return True

        except Exception:

            return False

    # ========================================================
    # SEND VLC COMMAND
    # ========================================================

    def send_command(self, command):

        if self.vlc_socket is None:

            if not self.start_vlc():

                return False

        try:

            self.vlc_socket.sendall(
                (command + "\n").encode()
            )

            return True

        except Exception:

            if self.connect_vlc():

                try:

                    self.vlc_socket.sendall(
                        (command + "\n").encode()
                    )

                    return True

                except Exception:

                    pass

            return False

    # ========================================================
    # REMEMBER ITEM
    # ========================================================

    def remember_item(self, item):

        self.last_items.append(item)

        if len(self.last_items) > self.history_limit:

            self.last_items.pop(0)

    # ========================================================
    # PLAY FILE
    # ========================================================

    def play_file(
        self,
        item,
        remember=True,
    ):

        if not self.start_vlc():

            return False

        path = item["path"]

        print(
            f"Tuesday: Playing {path.name}"
        )

        # Clear VLC playlist.

        self.send_command("clear")

        # Add file.

        if not self.send_command(
            f"add {path}"
        ):

            return False

        self.current_item = item

        self.paused = False

        if remember:

            self.remember_item(item)

        return True

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query,
        media_type=None,
    ):

        query = query.lower().strip()

        if not query:

            return []

        words = query.split()

        results = []

        for item in self.library:

            if (
                media_type is not None
                and item["type"] != media_type
            ):

                continue

            name = item["name"].lower()

            genre = item["genre"]

            score = 0

            # Exact phrase.

            if query in name:

                score += 10

            # Individual words.

            for word in words:

                if word in name:

                    score += 3

                if word == genre:

                    score += 5

            if score > 0:

                results.append(
                    (score, item)
                )

        results.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return [
            item
            for score, item in results
        ]

    # ========================================================
    # FIND GENRE
    # ========================================================

    def find_genre(self, query):

        query = query.lower().strip()

        matches = []

        for item in self.library:

            if item["type"] != "audio":

                continue

            genre = item["genre"]

            if not genre:

                continue

            if query == genre:

                matches.append(item)

        return matches

    # ========================================================
    # CHOOSE DIFFERENT ITEM
    # ========================================================

    def choose_different(
        self,
        items,
    ):

        if not items:

            return None

        # ----------------------------------------------------
        # Remove currently playing item.
        # ----------------------------------------------------

        candidates = [
            item
            for item in items
            if item != self.current_item
        ]

        # ----------------------------------------------------
        # Avoid recently played items when possible.
        # ----------------------------------------------------

        recent_paths = {
            item["path"]
            for item in self.last_items[-10:]
        }

        fresh = [
            item
            for item in candidates
            if item["path"] not in recent_paths
        ]

        if fresh:

            candidates = fresh

        if not candidates:

            # If everything has been played recently,
            # at least avoid the current item.

            candidates = [
                item
                for item in items
                if item != self.current_item
            ]

        if not candidates:

            candidates = items

        return random.choice(candidates)

    # ========================================================
    # PLAY QUERY
    # ========================================================

    def play(
        self,
        query,
        media_type="audio",
    ):

        query = query.lower().strip()

        # ----------------------------------------------------
        # Check if this is a genre.
        # ----------------------------------------------------

        genre_results = self.find_genre(query)

        if genre_results:

            self.play_mode = "genre"

            self.play_query = query

            item = self.choose_different(
                genre_results
            )

        else:

            # ------------------------------------------------
            # Normal search.
            # ------------------------------------------------

            results = self.search(
                query,
                media_type=media_type,
            )

            if not results:

                results = self.search(
                    query
                )

            if not results:

                return (
                    f"I couldn't find {query} "
                    "in your music library."
                )

            self.play_mode = "search"

            self.play_query = query

            # Prefer the best ten matches.

            top_results = results[:10]

            item = self.choose_different(
                top_results
            )

        if item is None:

            return (
                "I couldn't find another "
                "matching song."
            )

        if not self.play_file(item):

            return (
                "I couldn't start the media player."
            )

        return (
            f"Playing {item['name']}."
        )

    # ========================================================
    # RANDOM MUSIC
    # ========================================================

    def play_random(self):

        audio = [

            item

            for item in self.library

            if item["type"] == "audio"

        ]

        if not audio:

            return (
                "I couldn't find any music."
            )

        self.play_mode = "random"

        self.play_query = None

        item = self.choose_different(
            audio
        )

        if item is None:

            return (
                "I couldn't find another song."
            )

        if not self.play_file(item):

            return (
                "I couldn't start the media player."
            )

        return (
            f"Playing {item['name']}."
        )

    # ========================================================
    # RANDOM VIDEO
    # ========================================================

    def play_random_video(self):

        videos = [

            item

            for item in self.library

            if item["type"] == "video"

        ]

        if not videos:

            return (
                "I couldn't find any videos."
            )

        self.play_mode = "random_video"

        self.play_query = None

        item = self.choose_different(
            videos
        )

        if item is None:

            return (
                "I couldn't find another video."
            )

        if not self.play_file(item):

            return (
                "I couldn't start the media player."
            )

        return (
            f"Playing {item['name']}."
        )

    # ========================================================
    # NEXT
    # ========================================================

    def next_track(self):

        # ----------------------------------------------------
        # Nothing playing yet.
        # ----------------------------------------------------

        if self.current_item is None:

            return self.play_random()

        # ----------------------------------------------------
        # RANDOM MODE
        # ----------------------------------------------------

        if self.play_mode == "random":

            return self.play_random()

        # ----------------------------------------------------
        # RANDOM VIDEO MODE
        # ----------------------------------------------------

        if self.play_mode == "random_video":

            return self.play_random_video()

        # ----------------------------------------------------
        # GENRE MODE
        # ----------------------------------------------------

        if self.play_mode == "genre":

            matches = self.find_genre(
                self.play_query
            )

            if not matches:

                return (
                    "I couldn't find another "
                    "song in that genre."
                )

            item = self.choose_different(
                matches
            )

            if item is None:

                return (
                    "I couldn't find another "
                    "song in that genre."
                )

            if self.play_file(item):

                return (
                    f"Playing {item['name']}."
                )

            return (
                "I couldn't start the media player."
            )

        # ----------------------------------------------------
        # SEARCH MODE
        # ----------------------------------------------------

        if self.play_mode == "search":

            matches = self.search(
                self.play_query,
                media_type="audio",
            )

            if not matches:

                matches = self.search(
                    self.play_query
                )

            if not matches:

                return (
                    "I couldn't find another "
                    "matching song."
                )

            item = self.choose_different(
                matches[:10]
            )

            if item is None:

                return (
                    "I couldn't find another "
                    "matching song."
                )

            if self.play_file(item):

                return (
                    f"Playing {item['name']}."
                )

            return (
                "I couldn't start the media player."
            )

        # ----------------------------------------------------
        # No known mode.
        # ----------------------------------------------------

        return self.play_random()

    # ========================================================
    # PREVIOUS
    # ========================================================

    def previous_track(self):

        if len(self.last_items) < 2:

            return (
                "There isn't a previous song yet."
            )

        # Current item is the last history item.

        previous = self.last_items[-2]

        if self.play_file(
            previous,
            remember=False,
        ):

            # Remove current item from history.

            self.last_items.pop()

            return (
                f"Playing {previous['name']}."
            )

        return (
            "I couldn't go back."
        )

    # ========================================================
    # PAUSE
    # ========================================================

    def pause(self):

        if self.current_item is None:

            return "Nothing is playing."

        if self.paused:

            return (
                "The music is already paused."
            )

        if self.send_command("pause"):

            self.paused = True

            return "Paused."

        return (
            "I couldn't pause the music."
        )

    # ========================================================
    # RESUME
    # ========================================================

    def resume(self):

        if self.current_item is None:

            return "Nothing is playing."

        if not self.paused:

            return (
                "The music is already playing."
            )

        if self.send_command("pause"):

            self.paused = False

            return "Resuming."

        return (
            "I couldn't resume the music."
        )

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        if self.send_command("stop"):

            self.current_item = None

            self.paused = False

            return "Music stopped."

        return (
            "I couldn't stop the music."
        )

    # ========================================================
    # VOLUME
    # ========================================================

    def volume_up(self):

        if self.send_command("volup 1"):

            return "Volume up."

        return (
            "I couldn't change the volume."
        )

    def volume_down(self):

        if self.send_command("voldown 1"):

            return "Volume down."

        return (
            "I couldn't change the volume."
        )

    # ========================================================
    # CLOSE VLC
    # ========================================================

    def close(self):

        try:

            if self.vlc_socket is not None:

                self.send_command("quit")

                self.vlc_socket.close()

        except Exception:

            pass

        self.vlc_socket = None

        self.vlc_process = None


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()

    print("========================================")

    print(" Tuesday VLC controller test")

    print("========================================")

    media = TuesdayMedia()

    print()

    print("Testing random mode...")

    print(
        "Tuesday:",
        media.play_random()
    )

    print()

    print(
        "Mode:",
        media.play_mode
    )

    print()

    print("Testing NEXT...")

    print(
        "Tuesday:",
        media.next_track()
    )

    print()

    print(
        "Mode:",
        media.play_mode
    )

    print()

    print("Testing pop mode...")

    print(
        "Tuesday:",
        media.play("pop")
    )

    print()

    print(
        "Mode:",
        media.play_mode,
        "| Query:",
        media.play_query,
    )

    print()

    print("Testing NEXT pop...")

    print(
        "Tuesday:",
        media.next_track()
    )

    print()

    print("Testing Drake mode...")

    print(
        "Tuesday:",
        media.play("Drake")
    )

    print()

    print(
        "Mode:",
        media.play_mode,
        "| Query:",
        media.play_query,
    )

    print()

    print("Testing NEXT Drake...")

    print(
        "Tuesday:",
        media.next_track()
    )

    print()

    print("Testing previous...")

    print(
        "Tuesday:",
        media.previous_track()
    )

    print()

    print("Testing stop...")

    print(
        "Tuesday:",
        media.stop()
    )

    media.close()

    print()

    print("Media test finished.")