"""Creates (or checks) your Google Play upload key: a password-protected key file (PKCS#12, alias "upload") that the
GitHub build uses to sign the Play bundle. Run it on your own computer:

    uv run --no-project --with cryptography python mobile/play/make_upload_key.py

If a key already exists it asks for its password; a correct password keeps the key, otherwise the old key is renamed
(never deleted) and a new one is made. Then it walks you through the two GitHub secrets, putting the key and then the
password on the clipboard so nothing has to be typed into GitHub. Keep a copy of the key file and the password
somewhere safe: Google needs this same key for every update.
"""
import base64, datetime, getpass, subprocess, sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID


def make_key(password: bytes, years=30):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Beedo-Trade upload key")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=365 * years)).sign(key, hashes.SHA256()))
    return pkcs12.serialize_key_and_certificates(b"upload", key, cert, None, serialization.BestAvailableEncryption(password))


def password_ok(data: bytes, pw: str) -> bool:
    try:
        pkcs12.load_key_and_certificates(data, pw.encode())
        return True
    except Exception:
        return False


def clip(text: str):
    subprocess.run("clip", input=text.encode("utf-16-le"), check=True, shell=True)  # Windows clipboard


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "Beedo-Trade-keys" / "beedo-trade-upload-key.p12"
    pw = None
    if out.exists():
        print(f"You already have a key: {out}")
        pw = getpass.getpass("Type its password (nothing shows while you type), or just press Enter to make a new key: ")
        if pw and password_ok(out.read_bytes(), pw):
            print("Password CORRECT. Keeping this key.")
        else:
            old = out.with_name(f"old-{datetime.datetime.now():%Y%m%d-%H%M%S}-{out.name}")
            out.rename(old)  # never delete a key
            print(f"Making a new key. The old one was renamed to {old.name}.")
            pw = None
    if pw is None:
        pw = getpass.getpass("Choose a NEW password - English letters and numbers only, 8+ characters: ")
        if len(pw) < 8 or not pw.isascii() or pw != pw.strip() or pw != getpass.getpass("Type it again: "):
            sys.exit("Too short, not English letters/numbers, or the two didn't match. Nothing was saved; run me again.")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(make_key(pw.encode()))
        assert password_ok(out.read_bytes(), pw)
        print(f"Saved: {out}")
    clip(base64.b64encode(out.read_bytes()).decode())
    print("\nSTEP 1 of 2: the KEY is on the clipboard.")
    print("   On GitHub: Edit PLAY_UPLOAD_KEYSTORE > click the big box > Ctrl+A > Ctrl+V > Update secret.")
    input("   Then come back here and press Enter... ")
    clip(pw)
    print("STEP 2 of 2: the PASSWORD is on the clipboard.")
    print("   On GitHub: Edit PLAY_UPLOAD_PASSWORD > click the box > Ctrl+A > Ctrl+V > Update secret.")
    input("   Then come back here and press Enter... ")
    clip(" ")
    print("Done, clipboard cleared. Tell Claude: both updated.")


if __name__ == "__main__":
    main()
