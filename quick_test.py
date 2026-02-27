import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from modules.link_detector.url_reputation import aggregate_reputation

urls = [
    ("MALWARE TEST (Google)", "http://malware.testing.google.test/testing/malware/"),
    ("CLEAN (GitHub)",        "https://github.com"),
    ("PAYPAL TYPOSQUAT",      "https://paypa1.com/login"),
]

for label, url in urls:
    r = aggregate_reputation(url)
    print(f"--- {label} ---")
    print(f"Overall: {r['overall']}")
    for s in r["sources"]:
        print(f"  {s['source']}: {s['status']} | {s['details']}")
    print()
