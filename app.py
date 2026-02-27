from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Email ML predictor (loads ml_model.pkl from ROOT internally)
from modules.email_analyzer.predict import predict_email

# Link detector (rule-based + real-time reputation)
from modules.link_detector.url_checks import analyze_url
from modules.link_detector.verdict import link_verdict
from modules.link_detector.url_reputation import aggregate_reputation

# Document scanner (detection-only)
from modules.document_scanner.file_checks import analyze_file_properties
from modules.document_scanner.macro_scan import detect_macros
from modules.document_scanner.embedded_links import extract_embedded_urls

# Steganography (detection-only signals)
from modules.steganography_kit.image_analysis import detect_stego_signals
from modules.steganography_kit.metadata_check import extract_metadata_flags

# Risk engine
from modules.risk_engine.score import compute_risk

app = Flask(__name__)
CORS(app)


SCAN_HISTORY = []


def _utc_ts():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _add_history(entry_type: str, summary: str, risk: dict | None, details: dict | None = None):
    SCAN_HISTORY.append({
        "ts": _utc_ts(),
        "type": entry_type,
        "summary": summary,
        "risk": risk,
        "details": details or {}
    })

    if len(SCAN_HISTORY) > 250:
        del SCAN_HISTORY[: len(SCAN_HISTORY) - 250]


def json_error(message: str, status: int = 400):
    return jsonify({"ok": False, "error": message}), status


@app.route("/analyze-email", methods=["POST"])
def analyze_email():
    """
    Accepts JSON: { "email": "full email text" }
    Returns ML label, confidence, and risk (email weight = 50%).
    """
    if not request.is_json:
        return json_error("Content-Type must be application/json", 415)

    data = request.get_json(silent=True) or {}
    email_text = data.get("email", "").strip()
    if not email_text:
        return json_error("Field 'email' is required")

    email_res = predict_email(email_text)
    risk = compute_risk(email=email_res, link=None, document=None)

    _add_history(
        entry_type="email",
        summary=f"{email_res.get('label', 'unknown')} ({email_res.get('confidence', '-') }%)",
        risk=risk,
        details={"email": email_res}
    )

    return jsonify({
        "ok": True,
        "email": email_res,
        "risk": risk
    })


@app.route("/analyze", methods=["POST"])
def analyze_email_legacy():
    """Backward-compatible alias for older frontend code."""
    if not request.is_json:
        return json_error("Content-Type must be application/json", 415)

    data = request.get_json(silent=True) or {}
    email_text = data.get("email", "").strip()
    if not email_text:
        return json_error("Field 'email' is required")

    email_res = predict_email(email_text)
    verdict = (email_res.get("label") or "").lower()
    confidence = email_res.get("confidence")
    return jsonify({
        "verdict": verdict,
        "confidence": confidence
    })


@app.route("/scan-link", methods=["POST"])
def scan_link():
    """
    Accepts JSON: { "url": "http(s)://..." }
    Returns rule-based indicators, real-time reputation (GSB / VT / PhishTank),
    verdict, and risk score (link weight = 25%).
    """
    if not request.is_json:
        return json_error("Content-Type must be application/json", 415)

    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return json_error("Field 'url' is required")

    # Rule-based analysis (always runs, no API key needed)
    indicators = analyze_url(url)

    # Real-time reputation checks (graceful if keys missing)
    reputation = aggregate_reputation(url)

    # Boost verdict if reputation says malicious
    if reputation.get("overall") == "malicious":
        indicators.append({
            "type": "reputation_malicious",
            "details": "Flagged by real-time reputation APIs",
            "severity": "high"
        })
    elif reputation.get("overall") == "suspicious":
        indicators.append({
            "type": "reputation_suspicious",
            "details": "Flagged as suspicious by reputation APIs",
            "severity": "medium"
        })

    verdict = link_verdict(indicators)
    risk = compute_risk(email=None, link=verdict, document=None)

    _add_history(
        entry_type="link",
        summary=url,
        risk=risk,
        details={"url": url, "verdict": verdict, "indicators": indicators, "reputation": reputation}
    )

    return jsonify({
        "ok": True,
        "url": url,
        "indicators": indicators,
        "reputation": reputation,
        "verdict": verdict,
        "risk": risk
    })


@app.route("/scan-document", methods=["POST"])
def scan_document():
    """
    Detection-only: no file execution.
    Accepts JSON with filename, mime, size_bytes, optional head_base64 and contains_macro.
    Returns findings + risk (document weight = 25%).
    """
    if not request.is_json:
        return json_error("Content-Type must be application/json", 415)

    data = request.get_json(silent=True) or {}
    filename = (data.get("filename") or "").strip()
    mime = (data.get("mime") or "").strip()
    size_bytes = data.get("size_bytes")
    head_b64 = data.get("head_base64")
    contains_macro = data.get("contains_macro")

    if not filename or size_bytes is None:
        return json_error("Fields 'filename' and 'size_bytes' are required")

    file_props = analyze_file_properties(
        filename=filename,
        mime=mime,
        size_bytes=size_bytes,
        head_base64=head_b64
    )
    macro_info = detect_macros(filename=filename, explicit_macro_flag=contains_macro)
    embedded = extract_embedded_urls(filename=filename, head_base64=head_b64)

    document = {
        "file_checks": file_props,
        "macro_scan": macro_info,
        "embedded_links": embedded
    }

    risk = compute_risk(email=None, link=None, document=document)

    _add_history(
        entry_type="document",
        summary=filename,
        risk=risk,
        details={"filename": filename, "document": document}
    )

    return jsonify({
        "ok": True,
        "document": document,
        "risk": risk
    })


@app.route("/stego-scan", methods=["POST"])
def stego_scan():
    """
    Detection-only steganography check.
    Accepts JSON with filename, mime, size_bytes, optional width/height and head_base64.
    Returns heuristic indicators (not included in weighted risk by spec).
    """
    if not request.is_json:
        return json_error("Content-Type must be application/json", 415)

    data = request.get_json(silent=True) or {}
    filename = (data.get("filename") or "").strip()
    mime = (data.get("mime") or "").strip()
    size_bytes = data.get("size_bytes")
    width = data.get("width")
    height = data.get("height")
    head_b64 = data.get("head_base64")

    if not filename or size_bytes is None:
        return json_error("Fields 'filename' and 'size_bytes' are required")

    image_signals = detect_stego_signals(
        filename=filename,
        mime=mime,
        size_bytes=size_bytes,
        width=width,
        height=height,
        head_base64=head_b64,
    )
    meta_flags = extract_metadata_flags(
        filename=filename,
        mime=mime,
        head_base64=head_b64
    )

    _add_history(
        entry_type="stego",
        summary=filename,
        risk=None,
        details={
            "filename": filename,
            "steganography": {
                "signals": image_signals,
                "metadata_flags": meta_flags
            }
        }
    )

    return jsonify({
        "ok": True,
        "steganography": {
            "signals": image_signals,
            "metadata_flags": meta_flags
        }
    })


@app.route("/dashboard", methods=["GET"])
def dashboard():
    stats = {"total": len(SCAN_HISTORY), "HIGH": 0, "MEDIUM": 0, "LOW": 0, "NONE": 0}
    for e in SCAN_HISTORY:
        risk = e.get("risk")
        if not risk:
            stats["NONE"] += 1
            continue
        lvl = (risk.get("level") or "").upper()
        if lvl in stats:
            stats[lvl] += 1
        else:
            stats["NONE"] += 1

    return jsonify({
        "ok": True,
        "stats": stats,
        "recent": SCAN_HISTORY[-10:]
    })


@app.route("/reports", methods=["GET"])
def reports():
    return jsonify({
        "ok": True,
        "history": SCAN_HISTORY
    })


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
