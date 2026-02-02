import base64
import re

# Lightweight metadata flag extraction from initial bytes.
# Academic demo only; avoids third-party EXIF libraries.


def _safe_decode_head(head_base64: str) -> bytes:
    try:
        return base64.b64decode(head_base64 or "", validate=False)
    except Exception:
        return b""


def extract_metadata_flags(filename: str, mime: str, head_base64: str = None):
    """
    Return booleans for simple metadata presence indicators found in early bytes.
    We do not parse full EXIF; we only heuristically detect markers.
    """
    notes = []
    data = _safe_decode_head(head_base64) if head_base64 else b""
    has_exif = False
    camera_model_present = False
    gps_present = False

    # JPEG EXIF APP1 marker
    if data and b"Exif\x00\x00" in data[:2048]:
        has_exif = True
        notes.append("EXIF header marker detected in early bytes.")

    if data:
        if re.search(rb"Model\x00|Make\x00", data[:4096]):
            camera_model_present = True
        if b"GPS" in data[:4096]:
            gps_present = True

    return {
        "has_exif": has_exif,
        "camera_model_present": camera_model_present,
        "gps_present": gps_present,
        "notes": notes,
    }

