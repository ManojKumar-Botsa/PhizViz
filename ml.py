import pandas as pd
import re
import pickle
from urllib.parse import urlparse
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
from scipy.sparse import hstack

LABEL_MAP = {"safe": 0, "suspicious": 1, "phishing": 2}

SUSPICIOUS_PHRASES = [
    "verify your account", "urgent", "account suspended",
    "click here", "login", "password reset",
    "confirm your identity", "update billing"
]

def extract_urls(text):
    urls = re.findall(r'https?://[^\s]+?(?=[.,;!?\s]|$)', text)
    return urls

def get_domain(url):
    try:
        return urlparse(url).netloc.lower()
    except (ValueError, Exception):
        # Handle malformed URLs gracefully
        return ""

def structural_features(texts):
    features = []

    for text in texts:
        text = text.lower()
        urls = extract_urls(text)

        suspicious_count = sum(p in text for p in SUSPICIOUS_PHRASES)
        has_ip = int(any(re.search(r'\d+\.\d+\.\d+\.\d+', u) for u in urls))

        domains = [get_domain(u) for u in urls]
        domain_mismatch = int(len(set(domains)) > 1)

        features.append([
            suspicious_count,
            len(urls),
            domain_mismatch,
            has_ip
        ])

    return np.array(features)

# ================= LOAD DATA =================
df = pd.read_csv("dataset.csv")
texts = df["email_text"].astype(str)
labels = df["label"].map(LABEL_MAP)

print("\nDataset distribution:")
print(df["label"].value_counts())

# ================= NLP FEATURES =================
tfidf = TfidfVectorizer(
    max_features=2000,      # 🔥 reduced to avoid memorization
    ngram_range=(1, 1),
    stop_words="english",
    sublinear_tf=True
)

X_text = tfidf.fit_transform(texts)
X_struct = structural_features(texts)

X = hstack([X_text, X_struct])

# ================= TRAIN / TEST =================
X_train, X_test, y_train, y_test = train_test_split(
    X, labels,
    test_size=0.2,
    stratify=labels,
    random_state=42
)

model = HistGradientBoostingClassifier(
    max_depth=6,
    learning_rate=0.05,
    max_iter=300,
    random_state=42
)

model.fit(X_train.toarray(), y_train)

# ================= EVALUATION =================
preds = model.predict(X_test.toarray())

print("\nTest Accuracy:", accuracy_score(y_test, preds))
print("\nClassification Report:\n")
print(classification_report(
    y_test,
    preds,
    labels=[0, 1, 2],
    target_names=["safe", "suspicious", "phishing"],
    zero_division=0
))

# ================= CROSS VALIDATION =================
cv_scores = cross_val_score(
    model,
    X.toarray(),
    labels,
    cv=5,
    scoring="accuracy"
)

print("\nCross-Validation Accuracy:", round(cv_scores.mean(), 4))

# ================= SAVE MODEL =================
with open("ml_model.pkl", "wb") as f:
    pickle.dump((model, tfidf), f)

print("\n✅ FINAL MODEL SAVED (ml_model.pkl)")
