"""2.3.2: trial version and unlock codes (no network)."""
import datetime as dt, sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[1])]
from beedo_app import licence

SEED = bytes(range(32))  # a test key, not the developer's


def test_ed25519_matches_rfc8032():
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    assert licence.public_key(seed).hex() == "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    assert licence.sign(seed, b"").hex().startswith("e5564300c360ac729086e2cc806e828a")


def test_unlock_codes(monkeypatch):
    monkeypatch.setattr(licence, "PUBLIC_KEY", licence.public_key(SEED))
    code = licence.make_code(SEED, "ABCD-EFGH")
    assert licence.read_code(code, "ABCD-EFGH") == (True, None)
    assert licence.read_code(code.lower().replace("-", " "), "ABCD-EFGH")[0]  # pasted with other spacing
    assert not licence.read_code(code, "WXYZ-1234")[0]  # another device
    assert not licence.read_code(code[:-2] + "AA", "ABCD-EFGH")[0] and licence.read_code("hello", "X")[0] is False
    dated = licence.make_code(SEED, "ABCD-EFGH", dt.date(2027, 6, 30))
    assert licence.read_code(dated, "ABCD-EFGH") == (True, dt.date(2027, 6, 30))


def test_trial_locks_after_the_end_date(monkeypatch):
    monkeypatch.setattr(licence, "PUBLIC_KEY", licence.public_key(SEED))
    end = licence.TRIAL_END
    assert not licence.status("ABCD-EFGH", None, end)["locked"] and licence.status("ABCD-EFGH", None, end)["days_left"] == 0
    assert licence.status("ABCD-EFGH", None, end + dt.timedelta(days=1))["locked"]
    after = end + dt.timedelta(days=1)
    s = licence.status("ABCD-EFGH", licence.make_code(SEED, "ABCD-EFGH"), after)
    assert s["unlocked"] and not s["locked"]
    short = licence.make_code(SEED, "ABCD-EFGH", end)  # an unlock code that itself ended
    assert licence.status("ABCD-EFGH", short, after)["locked"]
    assert not licence.status("ABCD-EFGH", licence.make_code(SEED, "OTHR-DEVC"), after)["unlocked"]


def test_device_code_is_stable():
    a = licence.device_code("install-1")
    assert a == licence.device_code("install-1") and len(a) == 9 and a[4] == "-"
