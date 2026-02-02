import base64

# Detection-only stego indicators (no decoding or execution).
# Heuristics used for viva explanations:
#  - Size vs resolution mismatch (large file but low pixel count)
#  - Entropy proxy from the first 512 bytes (very rough)
#  - Magic header plausibility for common formats (JPEG/PNG/GIF)

JPEG = b"\xFF\xD8\xFF"
PNG = b"\x89PNG\r\n\x1a\n"
GIF = b"GIF8"


def _safe_decode_head(head_base64: str) -> bytes:
    try:
        return base64.b64decode(head_base64 or "", validate=False)
    except Exception:
        return b""


def _magic_type(head: bytes) -> str:
    if head.startswith(JPEG):
        return "jpeg"
    if head.startswith(PNG):
        return "png"
    if head.startswith(GIF):
        return "gif"
    return "unknown"


def detect_stego_signals(filename: str, mime: str, size_bytes: int, width=None, height=None, head_base64: str = None):
    """
    Returns a dictionary with heuristic indicators of hidden data.
    This is a detection-only approach and does not attempt decoding.
    """
    notes = []
    head = _safe_decode_head(head_base64) if head_base64 else b""
    magic = _magic_type(head) if head else "unknown"

    # Size vs resolution mismatch
    size_mismatch = False
    try:
        if width and height and size_bytes:
            pixels = int(width) * int(height)
            if size_bytes > 5 * 1024 * 1024 and pixels < 500_000:  # >5MB but <0.5MP
                size_mismatch = True
                notes.append("Large file with low resolution may indicate embedded data.")
    except Exception:
        notes.append("Could not evaluate size vs resolution.")

    # Entropy proxy on header sample
    entropy_hint = "unknown"
    if head:
        sample = head[:512]
        if sample:
            try:
                mean = sum(sample) / len(sample)
                var = sum((b - mean) ** 2 for b in sample) / len(sample)
                if var > 6000:
                    entropy_hint = "high"
                elif var > 3000:
                    entropy_hint = "medium"
                else:
                    entropy_hint = "low"
            except Exception:
                notes.append("Could not compute entropy proxy on header.")

    return {
        "magic": magic,
        "size_resolution_mismatch": size_mismatch,
        "entropy_hint": entropy_hint,
        "notes": notes,
    }

