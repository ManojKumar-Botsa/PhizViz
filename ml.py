import pickle
from sklearn.ensemble import RandomForestClassifier

X = [
    [0,0,0.0,0,0],      # safe
    [2,1,0.4,0,0],      # suspicious
    [5,3,0.9,0,0],      # phishing
]
y = ["safe","suspicious","phishing"]

clf = RandomForestClassifier(n_estimators=50, random_state=42)
clf.fit(X,y)

with open("ml_model.pkl","wb") as f:
    pickle.dump(clf,f)
