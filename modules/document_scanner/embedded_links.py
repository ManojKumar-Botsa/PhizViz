import base64
import re

# Detection-only: naive URL scanning in the provided header/first bytes.
URL_RE = re.compile(rb"https?://[^\s\"'>]+", re.IGNORECASE)


def _safe_decode_head(head_base64: str) -> bytes:
    try:
        return base64.b64decode(head_base64 or "", validate=False)
    except Exception:
        return b""


def extract_embedded_urls(filename: str, head_base64: str = None):
    """
    Returns a dict with 'found' and 'suspicious' URL lists found in the
    initial bytes (best-effort; academic demo only).
    Suspicious if URL contains IP-host or suspicious TLD.
    """
    data = _safe_decode_head(head_base64) if head_base64 else b""
    urls = []
    if data:
        for m in URL_RE.finditer(data):
            try:
                urls.append(m.group(0).decode("utf-8", errors="ignore"))
            except Exception:
                pass

    suspicious = []
    for u in urls:
        if re.search(r"\d+\.\d+\.\d+\.\d+", u):
            suspicious.append(u)
        if re.search(r"\.(zip|mov|tk|ml|ga|cf|gq|xyz|top|work|click)(/|$)", u, re.IGNORECASE):
            suspicious.append(u)

    return {
        "found": urls,
        "suspicious": sorted(set(suspicious))
    }

