# -*- coding: utf-8 -*-
"""
test_reputation.py
------------------
Quick standalone test for the URL reputation module.
Run with: python test_reputation.py

Flask does NOT need to be running for this test.
"""

import sys
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from modules.link_detector.url_reputation import aggregate_reputation

TEST_URLS = [
    {
        "label": "Google malware test URL  [expect: MALICIOUS on GSB]",
        "url": "http://malware.testing.google.test/testing/malware/",
    },
    {
        "label": "Google phishing test URL [expect: MALICIOUS on GSB]",
        "url": "http://phishing.testcases.01.phishtank.com/test_case_data/test_case_basic_1.html",
    },
    {
        "label": "Clean URL - GitHub       [expect: CLEAN / no threats]",
        "url": "https://github.com",
    },
    {
        "label": "Typosquatting URL        [expect: rule-based flag]",
        "url": "https://paypa1.com/login",
    },
]

STATUS_LABELS = {
    "malicious":    "[!!!] MALICIOUS",
    "suspicious":   "[ ! ] SUSPICIOUS",
    "clean":        "[ v ] CLEAN",
    "not_found":    "[ - ] NOT IN DB",
    "rate_limited": "[<<<] RATE LIMITED",
    "error":        "[ERR] ERROR",
    "unknown":      "[ ? ] UNKNOWN",
}


def run_tests():
    print("=" * 65)
    print("  PhishViz - URL Reputation API Test")
    print("=" * 65)

    for item in TEST_URLS:
        url   = item["url"]
        label = item["label"]
        print(f"\n>> {label}")
        print(f"   {url}")
        print("-" * 65)

        result  = aggregate_reputation(url)
        overall = result.get("overall", "unknown")
        print(f"   OVERALL : {STATUS_LABELS.get(overall, overall)}")
        print()

        for src in result.get("sources", []):
            status_label = STATUS_LABELS.get(src["status"], src["status"])
            source_name  = src["source"].replace("_", " ").title()
            print(f"   {source_name:<28} {status_label}")
            print(f"   {'':28} {src['details']}")

    print("\n" + "=" * 65)
    print("  Test complete.")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
