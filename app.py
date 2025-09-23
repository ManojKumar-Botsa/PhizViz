
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import os
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")


# === Configuration ===
BLACKLISTED_DOMAINS = {"verify-account-test.com", "malicious.ru", "phishybank.com"}
WHITELISTED_DOMAINS = {"google.com", "microsoft.com", "github.com", "paypal.com", "webmail-test.com"}

TRUSTED_SENDERS = {
    "support@google.com",
    "noreply@github.com",
    "security@microsoft.com",
    "no-reply@accounts.google.com"
     "support@localbookstore.com",
    "newsletter@craftycookies.net",
    "updates@greenenergyhub.org",
    "no-reply@techworkshop.io",
    "info@mountaintrails.co",
    "contact@urbanlibrary.org",
    "hello@petcarehub.com",
    "team@bookwormclub.net",
    "alerts@fitnesspro.co",
    "noreply@cookingcorner.io",
    "support@artisansmarket.org",
    "updates@greentechnews.com",
    "info@dailyjournals.net",
    "hello@citygardens.co",
    "contact@hikinghub.org",
    "newsletter@techsavvy.io",
    "team@biketravelers.net",
    "alerts@homebakers.co",
    "support@localfarmersmarket.org",
    "no-reply@mindfulreads.com",
    "updates@yogastudio.net",
    "info@communityevents.co",
    "hello@tinycafes.org",
    "contact@photoclub.io",
    "newsletter@creativewriters.net",
    "team@startupcorner.co",
    "alerts@localtheater.org",
    "support@charityconnect.net",
    "no-reply@gameguild.io",
    "updates@musicacademy.co",
    "info@languagehub.org",
    "hello@makerspace.net",
    "contact@localvolunteers.co",
    "newsletter@healthtips.org",
    "team@adventureclub.io",
    "alerts@wellnesshub.net",
    "support@bookswap.co",
    "no-reply@codingdojo.org",
    "updates@filmfanclub.net",
    "info@craftsmarket.co",
    "hello@localgardeners.io",
    "contact@hobbyhub.org",
    "newsletter@digitalart.net",
    "team@runnercommunity.co",
    "alerts@travelcircle.io",
    "support@photographyclub.net",
    "no-reply@meditationhub.co",
    "updates@techcircle.org",
    "info@localchefs.net",
    "hello@fitnesscircle.co",
    "contact@booklovershub.org",
    "support@localcafes.org",
    "newsletter@hobbycorner.net",
    "updates@communitylibrary.co",
    "no-reply@fitnesshub.io",
    "info@cityparks.org",
    "contact@petownersclub.net",
    "hello@bookclub.co",
    "team@artworkshop.org",
    "alerts@healthcircle.net",
    "noreply@codingacademy.io",
    "support@localfarm.org",
    "updates@greentech.org",
    "info@dailyjournals.co",
    "hello@gardeningclub.net",
    "contact@hikingtrails.org",
    "newsletter@techcircle.io",
    "team@biketravelers.co",
    "alerts@homebakers.org",
    "support@charityconnect.co",
    "no-reply@gamingguild.net",
    "updates@musicacademy.io",
    "info@languagehub.co",
    "hello@makerspace.org",
    "contact@volunteersclub.net",
    "newsletter@healthtips.co",
    "team@adventureclub.org",
    "alerts@wellnesshub.co",
    "support@bookswap.net",
    "no-reply@codingdojo.co",
    "updates@filmfanclub.org",
    "info@craftsmarket.net",
    "hello@localgardeners.co",
    "contact@hobbyhub.org",
    "newsletter@digitalart.co",
    "team@runnercommunity.org",
    "alerts@travelcircle.net",
    "support@photographyclub.co",
    "no-reply@meditationhub.org",
    "updates@techcircle.co",
    "info@localchefs.org",
    "hello@fitnesscircle.net",
    "contact@booklovershub.co",
    "newsletter@cookingclub.org",
    "team@startupcorner.io",
    "alerts@localtheater.co",
    "no-reply@google.com",
    "support@google.com",
    "security@google.com",
    "no-reply@accounts.google.com",
    "noreply@microsoft.com",
    "support@microsoft.com",
    "security@microsoft.com",
    "no-reply@outlook.com",
    "no-reply@office.com",
    "support@linkedin.com",
    "notifications@linkedin.com",
    "no-reply@github.com",
    "support@github.com",
    "security@github.com",
    "noreply@apple.com",
    "support@apple.com",
    "security@apple.com",
    "no-reply@icloud.com",
    "no-reply@facebook.com",
    "support@facebook.com",
    "security@facebook.com",
    "notifications@facebookmail.com",
    "noreply@instagram.com",
    "support@instagram.com",
    "security@instagram.com",
    "no-reply@twitter.com",
    "support@twitter.com",
    "security@twitter.com",
    "noreply@snapchat.com",
    "support@snapchat.com",
    "security@snapchat.com",
    "no-reply@whatsapp.com",
    "support@whatsapp.com",
    "security@whatsapp.com",
    "noreply@tiktok.com",
    "support@tiktok.com",
    "security@tiktok.com",
    "no-reply@amazon.com",
    "support@amazon.com",
    "security@amazon.com",
    "no-reply@amazonaws.com",
    "no-reply@ebay.com",
    "support@ebay.com",
    "security@ebay.com",
    "no-reply@paypal.com",
    "support@paypal.com",
    "security@paypal.com",
    "no-reply@stripe.com",
    "support@stripe.com",
    "security@stripe.com",
    "no-reply@airbnb.com",
    "support@airbnb.com",
    "security@airbnb.com",
    "no-reply@uber.com",
    "support@uber.com",
    "security@uber.com",
    "no-reply@lyft.com",
    "support@lyft.com",
    "security@lyft.com",
    "no-reply@netflix.com",
    "support@netflix.com",
    "security@netflix.com",
    "no-reply@spotify.com",
    "support@spotify.com",
    "security@spotify.com",
    "no-reply@slack.com",
    "support@slack.com",
    "security@slack.com",
    "no-reply@zoom.us",
    "support@zoom.us",
    "security@zoom.us",
    "no-reply@adobe.com",
    "support@adobe.com",
    "security@adobe.com",
    "no-reply@dropbox.com",
    "support@dropbox.com",
    "security@dropbox.com",
    "no-reply@squareup.com",
    "support@squareup.com",
    "security@squareup.com",
    "no-reply@intuit.com",
    "support@intuit.com",
    "security@intuit.com",
    "no-reply@oracle.com",
    "support@oracle.com",
    "security@oracle.com",
    "no-reply@sap.com",
    "support@sap.com",
    "security@sap.com",
    "no-reply@atlassian.com",
    "support@atlassian.com",
    "security@atlassian.com",
    "no-reply@trello.com",
    "support@trello.com",
    "security@trello.com"

}

SUSPICIOUS_PHRASES = [
    "verify your account", "urgent", "account suspended", "click here",
    "login immediately", "update your account", "confirm your identity", "password reset"
]

# === Helper Functions ===
def extract_urls(email_text):
    return re.findall(r'https?://[^\s]+', email_text)

def extract_sender_domain(email_text):
    match = re.search(r"From:\s*([^\n]+)", email_text, re.IGNORECASE)
    if match:
        sender = match.group(1).strip()
        domain_match = re.search(r"@([\w\.-]+)", sender)
        if domain_match:
            return sender, domain_match.group(1).lower()
    return None, None

def get_domain(url):
    return urlparse(url).netloc.lower()

def is_trusted_domain(domain):
    """Check exact or subdomain match."""
    for d in WHITELISTED_DOMAINS:
        if domain == d or domain.endswith("." + d):
            return True
    return False

def is_trusted_sender(sender_email, domain):
    """Sender is trusted if email is in list OR domain is whitelisted."""
    return (sender_email in TRUSTED_SENDERS) or (domain and is_trusted_domain(domain))

# === Advanced Analyzer ===
def analyze_email(email_text):
    explanation = []
    score = 0
    max_score = 25  # More accurate scaling

    sender_email, sender_domain = extract_sender_domain(email_text)
    urls = extract_urls(email_text)

    explanation.append(f"Sender: {sender_email if sender_email else 'Unknown'}")
    explanation.append(f"Sender Domain: {sender_domain if sender_domain else 'Unknown'}")
    explanation.append(f"URLs Detected: {len(urls)}")

    # Sender Reputation Check
    if is_trusted_sender(sender_email, sender_domain):
        explanation.append(f"✅ Sender verified or trusted: {sender_email or sender_domain}")
    elif sender_domain in BLACKLISTED_DOMAINS:
        explanation.append(f"🚨 Sender domain is blacklisted: {sender_domain}")
        score += 8
    else:
        explanation.append(f"⚠️ Sender domain not in trusted list: {sender_domain}")
        score += 4

    # URL Analysis
    for url in urls:
        domain = get_domain(url)
        if domain in BLACKLISTED_DOMAINS:
            explanation.append(f"🚨 Blacklisted domain link: {domain}")
            score += 8
        elif is_trusted_domain(domain):
            explanation.append(f"✅ Safe domain link: {domain}")
        else:
            explanation.append(f"⚠️ Unrecognized domain: {domain}")
            score += 3

        # Domain mismatch penalty only if neither trusted
        if sender_domain and domain != sender_domain:
            if not (is_trusted_domain(sender_domain) and is_trusted_domain(domain)):
                explanation.append(f"⚠️ Domain mismatch: sender={sender_domain}, link={domain}")
                score += 2

    # Suspicious Keywords
    found_phrases = [p for p in SUSPICIOUS_PHRASES if p in email_text.lower()]
    if found_phrases:
        if is_trusted_sender(sender_email, sender_domain):
            explanation.append(f"ℹ️ Security phrases found but sender trusted → minimal impact.")
            score += len(found_phrases) * 0.3
        else:
            explanation.append(f"⚠️ Suspicious phrases: {', '.join(found_phrases)}")
            score += len(found_phrases) * 1.5

    # Too Many Links Check
    if len(urls) > 5:
        explanation.append(f"⚠️ Too many links detected ({len(urls)})")
        score += 3

    # Risk Score & Verdict
    risk_percentage = min(int((score / max_score) * 100), 100)
    if score >= 12:
        verdict = "phishing"
    elif 6 <= score < 12:
        verdict = "suspicious"
    else:
        verdict = "safe"

    color = {"safe": "#28a745", "suspicious": "#ffc107", "phishing": "#dc3545"}[verdict]
    graph = [{"id": "user"}] + [{"id": url} for url in urls]

    explanation.append(f"Phishing Risk: {risk_percentage}%")
    explanation.append(f"Verdict: {verdict.upper()}")

    return {
        "verdict": verdict,
        "details": "\n".join(explanation),
        "risk_score": risk_percentage,
        "graph": graph,
        "color": color
    }

# === Flask Route ===
@app.route("/analyze", methods=["POST"])
def analyze_route():
    data = request.get_json()
    email = data.get("email", "")
    if not email.strip():
        return jsonify({"verdict": "unknown", "details": "No email content provided.", "graph": [], "color": "#6c757d"})
    return jsonify(analyze_email(email))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

