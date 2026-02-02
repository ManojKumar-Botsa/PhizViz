def link_verdict(indicators):
    """
    Convert indicators into a verdict and risk level.
    Mapping:
      - Any 'high' severity -> PHISHING, HIGH
      - Else if any indicator -> PHISHING, MEDIUM
      - Else -> SAFE, LOW
    """
    if not indicators:
        return {"verdict": "SAFE", "risk_level": "LOW"}

    severities = {str(i.get("severity", "")).lower() for i in indicators}
    if "high" in severities:
        return {"verdict": "PHISHING", "risk_level": "HIGH"}
    return {"verdict": "PHISHING", "risk_level": "MEDIUM"}

