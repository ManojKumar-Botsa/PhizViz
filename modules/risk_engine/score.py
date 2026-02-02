def _level(score_0_100: float) -> str:
    if score_0_100 >= 70:
        return "HIGH"
    if score_0_100 >= 40:
        return "MEDIUM"
    return "LOW"


def _email_component(email_result: dict) -> float:
    """Map ML label to a 0..1 risk component scaled by confidence."""
    if not email_result:
        return 0.0
    label = (email_result.get("label") or "").lower()
    conf = float(email_result.get("confidence") or 0.0) / 100.0
    if label == "phishing":
        base = 1.0
    elif label == "suspicious":
        base = 0.6
    else:
        base = 0.2
    return base * max(0.5, conf)


def _link_component(link_verdict: dict) -> float:
    if not link_verdict:
        return 0.0
    verdict = (link_verdict.get("verdict") or "").upper()
    level = (link_verdict.get("risk_level") or "").upper()
    if verdict != "PHISHING":
        return 0.1
    return 1.0 if level == "HIGH" else 0.6


def _document_component(document_result: dict) -> float:
    if not document_result:
        return 0.0

    file_checks = document_result.get("file_checks", {})
    macro_scan = document_result.get("macro_scan", {})
    embedded = document_result.get("embedded_links", {})

    score = 0.0
    if file_checks.get("signature_mismatch"):
        score += 0.5
    if file_checks.get("double_extension"):
        score += 0.4
    if file_checks.get("size_anomaly"):
        score += 0.2

    if macro_scan.get("suspected_macros"):
        score += 0.6

    if embedded.get("suspicious"):
        score += 0.4

    return min(1.0, score)


def compute_risk(email=None, link=None, document=None):
    """Combine components with weights: email 50%, link 25%, document 25%."""
    e = _email_component(email) if email else 0.0
    l = _link_component(link) if link else 0.0
    d = _document_component(document) if document else 0.0

    score = (0.50 * e + 0.25 * l + 0.25 * d) * 100.0
    return {"score": round(score, 2), "level": _level(score)}

