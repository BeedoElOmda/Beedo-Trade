"""Beedo-Trade on Android (and later iOS): the desktop app's own server (beedo_app.main.serve) runs in a background
thread and its pages show in a web view, so the engine, the checklist and the screens are exactly the desktop ones."""
import asyncio, os, socket, sys, threading, traceback
from pathlib import Path

import toga

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "engine"))  # analyze.py, fundamentals.py, metals.py, timemachine.py (copied at build time)
PORT = 8765
STARTING = """<html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;height:100vh;display:grid;place-items:center;background:linear-gradient(160deg,#3F70E6,#1D45A7 55%,#109EA5);color:#fff;font:16px sans-serif">
<div>{msg}</div></body></html>"""


def _engine():
    """Runs the desktop app's server; any start-up error goes to the log (logcat: python.stderr)."""
    try:
        from beedo_app import main  # after APPDATA is set: main reads it when it loads
        main.serve(port=PORT)
    except Exception:
        traceback.print_exc()


def _listening():
    try:
        socket.create_connection(("127.0.0.1", PORT), timeout=0.3).close()
        return True
    except OSError:
        return False


class BeedoTrade(toga.App):
    def startup(self):
        os.environ["APPDATA"] = str(self.paths.data)  # settings.json lives in the app's private storage
        threading.Thread(target=_engine, daemon=True).start()
        self.web = toga.WebView()
        self.web.set_content("http://127.0.0.1/", STARTING.replace("{msg}", "Starting Beedo-Trade…"))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.web
        self.main_window.show()
        try:  # the page draws its own top bar in the icon's gradient
            self._impl.native.getSupportActionBar().hide()
        except Exception:
            traceback.print_exc()
        self.loop.create_task(self._open())  # never block the screen while the engine starts

    async def _open(self):
        for _ in range(150):  # up to 30 s
            if _listening():
                self.web.url = f"http://127.0.0.1:{PORT}/index.html"
                return
            await asyncio.sleep(0.2)
        self.web.set_content("http://127.0.0.1/", STARTING.replace("{msg}", "Beedo-Trade could not start its engine. Close the app and open it again."))


def main():
    return BeedoTrade()
