import subprocess
from pathlib import Path


# ============================================================
# APPLICATION PATHS
# ============================================================

APPS = {

    "gta": Path(
    r"C:\Program Files (x86)\Grand Theft Auto V Legacy\PlayGTAV.bat"
    ),

    "gta 5": Path(
        r"C:\Program Files (x86)\Grand Theft Auto V Legacy\PlayGTAV.bat"
    ),

    "gta v": Path(
        r"C:\Program Files (x86)\Grand Theft Auto V Legacy\PlayGTAV.bat"
    ),

    "fifa": Path(
        r"C:\Program Files (x86)\FIFA19\FIFA19.exe"
    ),

    "fifa 19": Path(
        r"C:\Program Files (x86)\FIFA19\FIFA19.exe"
    ),
}


class TuesdayApps:

    def open_app(self, name):

        name = name.lower().strip()

        path = APPS.get(name)

        if path is None:

            return f"I don't know how to open {name}."

        if not path.exists():

            return f"I couldn't find {name} on this PC."

        try:

            if path.suffix.lower() == ".bat":

                subprocess.Popen(
                    ["cmd", "/c", str(path)]
                )

            else:

                subprocess.Popen(
                    [str(path)]
                )

            return f"Opening {name}."

        except Exception as e:

            print("App launch error:", e)

            return f"I couldn't open {name}."


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    apps = TuesdayApps()

    print(apps.open_app("gta"))
    print(apps.open_app("fifa 19"))