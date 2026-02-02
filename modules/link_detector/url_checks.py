import re
from urllib.parse import urlparse

# Rule-based URL analysis for academic phishing detection demos.

SHORTENER_DOMAINS = {
    "bit.ly", "goo.gl", "t.co", "ow.ly", "tinyurl.com",
    "is.gd", "buff.ly", "rebrand.ly", "cutt.ly", "shorte.st"
}

SUSPICIOUS_TLDS = {
    "zip", "mov", "tk", "ml", "ga", "cf", "gq",
    "xyz", "top", "work", "click", "country", "mom"
}

POPULAR_DOMAINS = {
    "google.com", "microsoft.com", "apple.com", "github.com",
    "facebook.com", "amazon.com", "paypal.com", "netflix.com",
    "linkedin.com", "youtube.com", "instagram.com"
}


def _levenshtein(a: str, b: str) -> int:
    """Lightweight edit distance; avoids external deps for viva."""
    a, b = (a or "").lower(), (b or "").lower()
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        prev = dp[0]
        dp[0] = i
        for j, cb in enumerate(b, start=1):
            cur = dp[j]
            dp[j] = min(
                dp[j] + 1,          # deletion
                dp[j - 1] + 1,      # insertion
                prev + (ca != cb)   # substitution
            )
            prev = cur
    return dp[-1]


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _tld(domain: str) -> str:
    parts = (domain or "").split(".")
    return parts[-1] if parts else ""


def analyze_url(url: str):
    """
    Return list of indicator dicts, e.g.:
      [{"type": "shortener", "details": "bit.ly", "severity": "medium"}, ...]
    """
    indicators = []
    d = _domain(url)
    tld = _tld(d)

    # 1) Shortened URLs
    if d in SHORTENER_DOMAINS:
        indicators.append({"type": "shortener", "details": d, "severity": "medium"})

    # 2) IP-based URLs (e.g., http://192.168.1.1/login)
    host_only = d.split(":")[0] if d else ""
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host_only):
        indicators.append({"type": "ip_address", "details": d, "severity": "high"})

    # 3) Suspicious TLDs
    if tld in SUSPICIOUS_TLDS:
        indicators.append({"type": "suspicious_tld", "details": tld, "severity": "medium"})

    # 4) Typosquatting vs popular brands
    for pd in POPULAR_DOMAINS:
        if _levenshtein(d, pd) <= 2 and d != pd:
            indicators.append({"type": "typosquatting", "details": f"{d} ~ {pd}", "severity": "high"})
            break

    # 5) Excessive subdomains (login.security.verify.paypal.com.attacker.tld)
    if d.count(".") >= 4:
        indicators.append({"type": "excessive_subdomains", "details": d, "severity": "medium"})

    return indicators

