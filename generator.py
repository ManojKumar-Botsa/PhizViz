import random
import csv

SAFE_TEMPLATES = [
    "Your order has been shipped successfully.",
    "Meeting scheduled for tomorrow at 10 AM.",
    "Your GitHub security alert was resolved.",
    "Monthly newsletter from your subscription.",
    "Invoice attached for your recent purchase.",
    "Your password was changed successfully.",
    "Security update regarding your account.",  # 🔥 overlap
]

SUSPICIOUS_TEMPLATES = [
    "We noticed unusual activity in your account.",
    "Please review recent changes to your profile.",
    "Login attempt detected. Check your account.",
    "Action required to avoid service interruption.",
    "Security notice regarding your account access."
]

PHISHING_TEMPLATES = [
    "Urgent! Verify your account immediately {url}",
    "Your account has been suspended. Click here {url}",
    "Reset your password now to regain access {url}",
    "Confirm your identity to avoid account lock {url}",
    "Update billing information immediately {url}"
]

SAFE_URLS = [
    "https://google.com",
    "https://github.com",
    "https://paypal.com",
    "https://microsoft.com",
]

PHISHING_URLS = [
    "http://secure-login.ru",
    "http://verify-account-test.com/login",
    "http://192.168.1.45/verify",
    "http://bank-update.phishybank.com",
]

def generate_dataset(total_samples=6000):
    rows = []

    for _ in range(total_samples):
        r = random.random()

        # SAFE
        if r < 0.4:
            text = random.choice(SAFE_TEMPLATES)

            # 🔥 noise: safe email with security words or URL
            if random.random() < 0.25:
                text += " " + random.choice(SAFE_URLS)

            label = "safe"

        # SUSPICIOUS
        elif r < 0.65:
            text = random.choice(SUSPICIOUS_TEMPLATES)

            # 🔥 noise: suspicious email with phishing-like URL
            if random.random() < 0.3:
                text += " " + random.choice(PHISHING_URLS)

            label = "suspicious"

        # PHISHING
        else:
            text = random.choice(PHISHING_TEMPLATES).format(
                url=random.choice(PHISHING_URLS)
            )

            # 🔥 noise: phishing email without URL
            if random.random() < 0.2:
                text = text.replace("{url}", "")

            label = "phishing"

        rows.append([text.strip(), label])

    return rows

with open("dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["email_text", "label"])
    writer.writerows(generate_dataset())

print("✅ Realistic dataset generated (with noise & overlap)")
