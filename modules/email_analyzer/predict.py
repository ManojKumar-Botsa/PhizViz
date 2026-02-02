import pickle
import re
from urllib.parse import urlparse
import numpy as np

# Labels used during training
LABELS = ["safe", "suspicious", "phishing"]

# Linguistic/structural hints aligned with training
SUSPICIOUS_PHRASES = [
    "verify your account", "urgent", "account suspended",
    "click here", "login", "password reset",
    "confirm your identity", "update billing"
]


def _extract_urls(text: str):
    # Extract URLs avoiding trailing punctuation
    return re.findall(r'https?://[^\s]+?(?=[.,;!?\s]|$)', text or "")


def _get_domain(url: str):
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _structural_features(email_text: str) -> np.ndarray:
    """MUST match structural feature order used during training."""
    t = (email_text or "").lower()
    urls = _extract_urls(t)

    suspicious_count = sum(p in t for p in SUSPICIOUS_PHRASES)
    has_ip = int(any(re.search(r'\d+\.\d+\.\d+\.\d+', u) for u in urls))

    domains = [_get_domain(u) for u in urls]
    domain_mismatch = int(len(set(domains)) > 1)

    # [suspicious_phrase_count, url_count, domain_mismatch, has_ip]
    return np.array([[suspicious_count, len(urls), domain_mismatch, has_ip]])


# Load ML artifacts from ROOT (no retraining or moving)
with open("ml_model.pkl", "rb") as f:
    model, tfidf = pickle.load(f)


def predict_email(email_text: str):
    """
    Returns:
      { "label": <str>, "confidence": <float 0-100> }
    Explanation:
    - Text features via TF-IDF (loaded from pickle)
    - Structural features via phishing heuristics
    - Concatenation mirrors training pipeline
    """
    text_features = tfidf.transform([email_text or ""])
    struct = _structural_features(email_text)
    X = np.hstack([text_features.toarray(), struct])

    pred_idx = int(model.predict(X)[0])
    try:
        proba = model.predict_proba(X)[0]
        conf = float(np.max(proba)) * 100.0
    except Exception:
        # Fallback if estimator lacks predict_proba
        conf = 100.0 if pred_idx == 2 else 70.0 if pred_idx == 1 else 90.0

    return {
        "label": LABELS[pred_idx],
        "confidence": round(conf, 2)
    }
