

import os
import hashlib
import requests
from dotenv import load_dotenv

# Load .env file for API keys
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(_ROOT, ".env"))

GOOGLE_API_KEY   = os.getenv("GOOGLE_SAFE_BROWSING_KEY", "")
VIRUSTOTAL_KEY   = os.getenv("VIRUSTOTAL_KEY", "")

_TIMEOUT = 8  # seconds per request



def check_google_safe_browsing(url: str) -> dict:
    """
    Lookup URL against Google Safe Browsing threat lists.
    Docs: https://developers.google.com/safe-browsing/v4/lookup-api
    """
    source = "google_safe_browsing"

    if not GOOGLE_API_KEY:
        return _result(source, "error", "GOOGLE_SAFE_BROWSING_KEY not set in .env")

    endpoint = (
        f"https://safebrowsing.googleapis.com/v4/threatMatches:find"
        f"?key={GOOGLE_API_KEY}"
    )
    payload = {
        "client": {"clientId": "phishviz", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE", "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        resp = requests.post(endpoint, json=payload, timeout=_TIMEOUT)
        if resp.status_code == 429:
            return _result(source, "rate_limited", "Quota exceeded", {})
        resp.raise_for_status()
        data = resp.json()

        if data.get("matches"):
            threats = [m.get("threatType", "UNKNOWN") for m in data["matches"]]
            return _result(source, "malicious", f"Threats: {', '.join(threats)}", data)

        return _result(source, "clean", "No threats found", data)

    except requests.exceptions.Timeout:
        return _result(source, "error", "Request timed out")
    except requests.exceptions.RequestException as e:
        return _result(source, "error", str(e))



def check_virustotal(url: str) -> dict:
    """
    Submit a URL to VirusTotal and get aggregated scan results.
    Free tier: 4 requests/minute.
    Docs: https://developers.virustotal.com/reference/url-info
    """
    source = "virustotal"

    if not VIRUSTOTAL_KEY:
        return _result(source, "error", "VIRUSTOTAL_KEY not set in .env")

    headers = {"x-apikey": VIRUSTOTAL_KEY}

   
    url_id = _vt_url_id(url)
    endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"

    try:
        resp = requests.get(endpoint, headers=headers, timeout=_TIMEOUT)

        if resp.status_code == 429:
            return _result(source, "rate_limited", "Rate limit reached (4 req/min on free tier)")

        if resp.status_code == 404:
           
            sub = requests.post(
                "https://www.virustotal.com/api/v3/urls",
                headers=headers,
                data={"url": url},
                timeout=_TIMEOUT
            )
            if sub.status_code == 429:
                return _result(source, "rate_limited", "Rate limit on submission")
            return _result(source, "not_found", "URL submitted for scanning; retry in ~60s")

        resp.raise_for_status()
        data = resp.json()

        stats = (
            data.get("data", {})
                .get("attributes", {})
                .get("last_analysis_stats", {})
        )
        malicious  = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        total      = sum(stats.values()) or 1

        if malicious > 0:
            return _result(
                source, "malicious",
                f"{malicious}/{total} engines flagged as malicious",
                stats
            )
        if suspicious > 0:
            return _result(
                source, "suspicious",
                f"{suspicious}/{total} engines flagged as suspicious",
                stats
            )
        return _result(source, "clean", f"0/{total} engines flagged", stats)

    except requests.exceptions.Timeout:
        return _result(source, "error", "Request timed out")
    except requests.exceptions.RequestException as e:
        return _result(source, "error", str(e))



def check_phishtank(url: str) -> dict:
    
    source = "phishtank"
    endpoint = "https://checkurl.phishtank.com/checkurl/"

    try:
        resp = requests.post(
            endpoint,
            data={
                "url": url,
                "format": "json",
                "app_key": ""   
            },
            timeout=_TIMEOUT
        )

        if resp.status_code == 429:
            return _result(source, "rate_limited", "Too many requests to PhishTank")

        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", {})

        if results.get("in_database"):
            if results.get("valid"):
                return _result(
                    source, "malicious",
                    f"Confirmed phish (submitted: {results.get('submitted_at', 'unknown')})",
                    results
                )
            else:
                return _result(source, "clean", "In database but marked invalid/clean", results)

        return _result(source, "clean", "Not found in PhishTank database", results)

    except requests.exceptions.Timeout:
        return _result(source, "error", "Request timed out")
    except requests.exceptions.RequestException as e:
        return _result(source, "error", str(e))



def aggregate_reputation(url: str) -> dict:
   
    results = [
        check_google_safe_browsing(url),
        check_virustotal(url),
        check_phishtank(url),
    ]

    statuses = {r["status"] for r in results}

    if "malicious" in statuses:
        overall = "malicious"
    elif "suspicious" in statuses:
        overall = "suspicious"
    elif statuses <= {"clean", "not_found", "rate_limited"}:
        overall = "clean"
    else:
        overall = "unknown"

    return {"overall": overall, "sources": results}


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def _result(source: str, status: str, details: str, raw=None) -> dict:
    return {"source": source, "status": status, "details": details, "raw": raw}


def _vt_url_id(url: str) -> str:
    """
    VirusTotal v3 expects the URL to be base64url-encoded (no padding).
    As a safe fallback we use the SHA-256 hex digest which VT also accepts.
    """
    import base64
    encoded = base64.urlsafe_b64encode(url.encode()).rstrip(b"=").decode()
    return encoded
