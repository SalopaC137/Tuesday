import os
import subprocess


class TuesdayPC:

    def open_chrome(self):
        subprocess.Popen(
            ["cmd", "/c", "start", "", "chrome"],
            shell=False,
        )
        return "Opening Chrome."

    def open_notepad(self):
        subprocess.Popen(
            ["notepad.exe"],
            shell=False,
        )
        return "Opening Notepad."

    def open_calculator(self):
        subprocess.Popen(
            ["calc.exe"],
            shell=False,
        )
        return "Opening Calculator."

    def open_downloads(self):

        downloads = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
        )

        os.startfile(downloads)

        return "Opening your Downloads folder."