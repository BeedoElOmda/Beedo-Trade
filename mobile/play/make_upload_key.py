"""Creates your Google Play upload key: a password-protected key file (PKCS#12, alias "upload") that the GitHub build
uses to sign the Play bundle. Run it once, on your own computer:

    uv run --with cryptography python mobile/play/make_upload_key.py

It asks for a password (typed twice, not shown) and saves the key in Documents\\Beedo-Trade-keys. Keep a copy of that
file and the password somewhere safe: Google needs this same key for every update. It also copies the key, as text, to
the clipboard, ready to paste into the GitHub secret PLAY_UPLOAD_KEYSTORE.
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


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "Beedo-Trade-keys" / "beedo-trade-upload-key.p12"
    if out.exists():
        sys.exit(f"{out} already exists. Keep using it: Google Play needs the same upload key for every update.")
    pw = getpass.getpass("Choose a password for the upload key (8+ characters): ")
    if len(pw) < 8 or pw != getpass.getpass("Type it again: "):
        sys.exit("The passwords were too short or didn't match. Nothing was saved.")
    data = make_key(pw.encode())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"Saved: {out}")
    b64 = base64.b64encode(data).decode()
    try:
        subprocess.run("clip", input=b64.encode("utf-16-le"), check=True, shell=True)  # Windows clipboard
        print("The key is on the clipboard: paste it into the GitHub secret PLAY_UPLOAD_KEYSTORE.")
    except Exception:
        (out.parent / "PLAY_UPLOAD_KEYSTORE.txt").write_text(b64)
        print(f"Paste the text in {out.parent / 'PLAY_UPLOAD_KEYSTORE.txt'} into the GitHub secret PLAY_UPLOAD_KEYSTORE, then delete that file.")
    print("Put the same password into the GitHub secret PLAY_UPLOAD_PASSWORD.")


if __name__ == "__main__":
    main()
