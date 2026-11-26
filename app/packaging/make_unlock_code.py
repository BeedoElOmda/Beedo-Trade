"""Makes an unlock code for one device of the Mo'ashir Trade trial. For the developer only.

  python app/packaging/make_unlock_code.py ABCD-EFGH              unlock with no end date
  python app/packaging/make_unlock_code.py ABCD-EFGH 2027-12-31   unlock until that date

The device code is shown on the user's lock screen and on the About page. The code is printed and copied to the
clipboard. The private key is Documents/Beedo-Trade-keys/unlock-key.txt: never share it, never put it in the repo.
Losing it means old codes keep working but no new ones can be made (a new key needs a new app version)."""
import datetime as dt, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from beedo_app import licence  # noqa: E402

KEY = Path.home() / "Documents" / "Beedo-Trade-keys" / "unlock-key.txt"


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--new-key":
        if KEY.exists():
            sys.exit(f"{KEY} already exists: keep using it.")
        import os
        KEY.parent.mkdir(parents=True, exist_ok=True)
        seed = os.urandom(32)
        KEY.write_text(seed.hex(), encoding="ascii")
        print("Private key saved to", KEY)
        print("PUBLIC_KEY for beedo_app/licence.py:", licence.public_key(seed).hex())
        return
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    device = sys.argv[1].strip().upper()
    if len(device) != 9 or device[4] != "-":
        sys.exit("The device code looks like ABCD-EFGH.")
    until = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) == 3 else None
    seed = bytes.fromhex(KEY.read_text(encoding="ascii").strip())
    if licence.public_key(seed) != licence.PUBLIC_KEY:
        sys.exit("This private key doesn't match the app's public key.")
    code = licence.make_code(seed, device, until)
    assert licence.read_code(code, device) == (True, until)
    print(f"Unlock code for {device}" + (f", until {until}" if until else ", no end date") + ":\n\n" + code + "\n")
    try:
        subprocess.run("clip", input=code, text=True, check=True, shell=True)
        print("Copied to the clipboard.")
    except Exception:
        pass


if __name__ == "__main__":
    main()
