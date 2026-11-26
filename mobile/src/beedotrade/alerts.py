"""Alerts as Android notifications: the daily background check (run by AlertWorker.java, also when the app is closed)
and the notifier the app's own 15-minute check uses while it is open."""
import os, sys, time, zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKER = "io.github.beedoelomda.beedotrade.AlertWorker"


def notifier(ctx):
    """main.NOTIFY: one Android notification per alert."""
    from java import jclass
    worker = jclass(WORKER)

    def notify(hit):
        worker.show(ctx, zlib.crc32(hit["text"].encode()) & 0x7FFFFFFF, f"Mo'ashir Trade: {hit['symbol']}", hit["text"])
    return notify


def run(ctx):
    """The daily check after the close. Settings live where the app keeps them (Toga's paths.data = files/data)."""
    os.environ.setdefault("APPDATA", str(Path(ctx.getFilesDir().getPath()) / "data"))
    if str(HERE / "engine") not in sys.path:
        sys.path.insert(0, str(HERE / "engine"))
    from beedo_app import main
    main.NOTIFY = notifier(ctx)
    if os.environ.get("BEEDO_TEST_NOTIFY"):  # emulator test: prove a notification can be shown
        main.NOTIFY({"symbol": "TEST", "text": "Notifications work. Your alerts will appear here."})
    elif time.gmtime(time.time() + 2 * 3600).tm_wday in (4, 5):  # Friday and Saturday in Cairo: the EGX is closed
        print("Beedo-Trade alert check: the market is closed today")
        return
    r = main.Api().check_alerts()
    print(f"Beedo-Trade alert check: {r['checked']} stocks checked, {len(r['hits'])} alerts")
