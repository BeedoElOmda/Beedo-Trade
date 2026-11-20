"""Beedo-Trade on Android (and later iOS): the desktop app's own server (beedo_app.main.serve) runs in a background
thread and its pages show in a web view, so the engine, the checklist and the screens are exactly the desktop ones."""
import os, socket, sys, threading, time
from pathlib import Path

import toga

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "engine"))  # analyze.py, fundamentals.py, metals.py, timemachine.py (copied at build time)
PORT = 8765


def _wait_for_server(seconds=15):
    end = time.time() + seconds
    while time.time() < end:
        try:
            socket.create_connection(("127.0.0.1", PORT), timeout=0.5).close()
            return True
        except OSError:
            time.sleep(0.2)
    return False


class BeedoTrade(toga.App):
    def startup(self):
        os.environ["APPDATA"] = str(self.paths.data)  # settings.json lives in the app's private storage
        from beedo_app import main  # after APPDATA is set: main reads it when it loads
        threading.Thread(target=main.serve, kwargs={"port": PORT}, daemon=True).start()
        self.main_window = toga.MainWindow(title=self.formal_name)
        if _wait_for_server():
            self.main_window.content = toga.WebView(url=f"http://127.0.0.1:{PORT}/index.html")
        else:
            self.main_window.content = toga.Label("Beedo-Trade could not start its engine. Close the app and open it again.")
        self.main_window.show()


def main():
    return BeedoTrade()
