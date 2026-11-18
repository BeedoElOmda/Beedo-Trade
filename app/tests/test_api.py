"""pywebview exposes every public attribute of the js_api object to the page and walks into nested objects.
A public non-function attribute (such as the window) made it crawl .NET objects at start-up and freeze the app."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "skills" / "beedo-trade" / "scripts"), str(ROOT / "app")]
from beedo_app.main import Api


def test_api_exposes_only_methods():
    api = Api()
    api._window = object()  # what main() assigns at run time
    public = [n for n in dir(api) if not n.startswith("_")]
    assert public and all(callable(getattr(api, n)) for n in public), [n for n in public if not callable(getattr(api, n))]


def test_https_uses_bundled_certificates():
    """1.5.0 on macOS: no root certificates in the packaged app, so every download failed."""
    import os, ssl
    assert os.path.isfile(os.environ["SSL_CERT_FILE"])
    assert ssl.create_default_context().cert_store_stats()["x509_ca"] > 100
