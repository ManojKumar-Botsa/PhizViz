import base64

# Detection-only checks. We do not execute files.

PDF_MAGIC = b"%PDF-"
DOC_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")[:8]  # CFBF header (first 8 bytes)
ZIP_MAGIC = b"PK\x03\x04"  # OOXML (DOCX) is ZIP


def _safe_decode_head(head_base64: str) -> bytes:
    try:
        return base64.b64decode(head_base64 or "", validate=False)
    except Exception:
        return b""


def _double_extension(filename: str) -> bool:
    lower = (filename or "").lower()
    parts = lower.split(".")
    if len(parts) <= 2:
        return False
    executable_exts = {"exe", "bat", "cmd", "vbs", "js", "scr", "ps1"}
    doc_like = {"pdf", "doc", "docx"}
    final = parts[-1]
    prev = parts[-2]
    return final in executable_exts and prev in doc_like


def _signature_mismatch(mime: str, head: bytes) -> str:
    m = (mime or "").lower()
    if m == "application/pdf":
        if not head.startswith(PDF_MAGIC):
            return "Expected PDF magic header"
    elif m in {"application/msword", "application/doc"}:
        if not head.startswith(DOC_MAGIC):
            return "Expected OLE/CFBF (DOC) header"
    elif m in {"application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/zip"}:
        if not head.startswith(ZIP_MAGIC):
            return "Expected ZIP (DOCX) header"
    return ""


def analyze_file_properties(filename: str, mime: str, size_bytes: int, head_base64: str = None):
    """
    Returns a dict with detection findings for double extensions, signature mismatch,
    and size anomalies. We only inspect metadata/headers; no execution.
    """
    head = _safe_decode_head(head_base64) if head_base64 else b""

    notes = []
    double_ext = _double_extension(filename)

    mismatch_reason = _signature_mismatch(mime, head) if head else ""
    signature_mismatch = bool(mismatch_reason)
    if not head:
        notes.append("No header bytes provided; signature checks limited.")

    size_anomaly = False
    try:
        if size_bytes < 1024:
            size_anomaly = True
            notes.append("File size unusually small (<1KB).")
        elif size_bytes > 25 * 1024 * 1024:
            size_anomaly = True
            notes.append("File size unusually large (>25MB).")
    except Exception:
        notes.append("Invalid 'size_bytes' value.")

    return {
        "filename": filename,
        "size_bytes": size_bytes,
        "double_extension": double_ext,
        "signature_mismatch": signature_mismatch,
        "mismatch_reason": mismatch_reason,
        "size_anomaly": size_anomaly,
        "notes": notes,
    }

