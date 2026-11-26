"""Trial version: every copy works until TRIAL_END; after that it needs an unlock code made for its device code.

Unlock codes are Ed25519 signatures (RFC 8032) made with the developer's private key, which never leaves the developer's
PC (app/packaging/make_unlock_code.py). The app holds only the public key, so the open source code can check a code but
cannot make one. Pure Python: no extra package on Windows, Mac or Android."""
import base64, datetime as dt, hashlib, os, subprocess, sys

TRIAL_END = dt.date(2027, 1, 26)  # 2 months after 2.3.2; a later version can move it
PUBLIC_KEY = bytes.fromhex("8d205dcbe0b81eed410d8dc8710460bab542a07fe57acd46ee792e9820569295")
EPOCH = dt.date(2026, 1, 1)  # unlock-code end dates are stored as days after this

# ---------- Ed25519 (RFC 8032 reference arithmetic) ----------
_p = 2 ** 255 - 19
_q = 2 ** 252 + 27742317777372353535851937790883648493
_d = -121665 * pow(121666, _p - 2, _p) % _p
_I = pow(2, (_p - 1) // 4, _p)


def _H(m):
    return hashlib.sha512(m).digest()


def _x(y, sign):
    xx = (y * y - 1) * pow(_d * y * y + 1, _p - 2, _p) % _p
    x = pow(xx, (_p + 3) // 8, _p)
    if (x * x - xx) % _p:
        x = x * _I % _p
    if (x * x - xx) % _p:
        return None  # not a point on the curve
    return _p - x if (x & 1) != sign else x


def _add(P, Q):
    x1, y1, z1, t1 = P
    x2, y2, z2, t2 = Q
    a, b = (y1 - x1) * (y2 - x2) % _p, (y1 + x1) * (y2 + x2) % _p
    c, d = t1 * 2 * _d * t2 % _p, z1 * 2 * z2 % _p
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % _p, g * h % _p, f * g % _p, e * h % _p)


def _mul(s, P):
    Q = (0, 1, 1, 0)
    while s:
        if s & 1:
            Q = _add(Q, P)
        P, s = _add(P, P), s >> 1
    return Q


_By = 4 * pow(5, _p - 2, _p) % _p
_B = (_x(_By, 0), _By, 1, _x(_By, 0) * _By % _p)


def _enc(P):
    x, y, z, _ = P
    zi = pow(z, _p - 2, _p)
    x, y = x * zi % _p, y * zi % _p
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _dec(s):
    y = int.from_bytes(s, "little")
    sign, y = y >> 255, y & ((1 << 255) - 1)
    x = _x(y, sign) if y < _p else None
    return None if x is None else (x, y, 1, x * y % _p)


def _secret(seed):
    h = _H(seed)
    a = int.from_bytes(h[:32], "little") & ((1 << 254) - 8) | (1 << 254)
    return a, h[32:]


def public_key(seed):
    return _enc(_mul(_secret(seed)[0], _B))


def sign(seed, msg):
    a, prefix = _secret(seed)
    A = public_key(seed)
    r = int.from_bytes(_H(prefix + msg), "little") % _q
    R = _enc(_mul(r, _B))
    k = int.from_bytes(_H(R + A + msg), "little") % _q
    return R + ((r + k * a) % _q).to_bytes(32, "little")


def verify(pub, msg, sig):
    if len(sig) != 64 or len(pub) != 32:
        return False
    R, A, S = _dec(sig[:32]), _dec(pub), int.from_bytes(sig[32:], "little")
    if R is None or A is None or S >= _q:
        return False
    k = int.from_bytes(_H(sig[:32] + pub + msg), "little") % _q
    return _enc(_mul(S, _B)) == _enc(_add(R, _mul(k, A)))


# ---------- device code ----------
def _machine_id():
    try:
        if sys.platform == "win32":
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography",
                                0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as k:
                return winreg.QueryValueEx(k, "MachineGuid")[0]
        if sys.platform == "darwin":
            out = subprocess.run(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], capture_output=True, text=True, timeout=5).stdout
            return next(line.split('"')[-2] for line in out.splitlines() if "IOPlatformUUID" in line)
    except Exception:
        pass
    return None  # Android or unknown: the caller's saved random id is used


def device_code(install_id):
    """Eight letters/digits, the same on every start on this computer (Android: on this installation)."""
    raw = _machine_id() or install_id
    c = base64.b32encode(hashlib.sha256(f"moashir-trade|{raw}".encode()).digest()).decode()[:8]
    return f"{c[:4]}-{c[4:]}"


def new_install_id():
    return os.urandom(16).hex()


# ---------- unlock codes ----------
def _msg(device, days):
    return f"MOASHIR-TRADE|{device}|{days}".encode()


def make_code(seed, device, until=None):
    days = (until - EPOCH).days if until else 0  # 0 = no end date
    raw = base64.b32encode(days.to_bytes(2, "big") + sign(seed, _msg(device, days))).decode().rstrip("=")
    return "-".join(raw[i:i + 6] for i in range(0, len(raw), 6))


def read_code(code, device):
    """(valid for this device, end date or None). A valid code with a past end date is still returned as valid."""
    s = "".join(ch for ch in (code or "").upper() if ch.isalnum())
    try:
        raw = base64.b32decode(s + "=" * (-len(s) % 8))
    except (ValueError, TypeError):
        return False, None
    if len(raw) != 66:
        return False, None
    days = int.from_bytes(raw[:2], "big")
    return verify(PUBLIC_KEY, _msg(device, days), raw[2:]), (EPOCH + dt.timedelta(days=days) if days else None)


def status(device, code, today=None):
    today = today or dt.date.today()
    ok, until = read_code(code, device) if code else (False, None)
    unlocked = ok and (until is None or today <= until)
    return {"end": TRIAL_END.isoformat(), "days_left": max(0, (TRIAL_END - today).days), "device": device,
            "unlocked": unlocked, "until": until.isoformat() if unlocked and until else None,
            "locked": today > TRIAL_END and not unlocked}
