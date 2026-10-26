# src/analyze.py
import joblib
import pandas as pd
from src.preprocess import load_nsl_kdd, COLUMNS

from src.train import align_columns

model = joblib.load("models/random_forest.joblib")

X_train, _ = load_nsl_kdd("data/KDDTrain+.txt")
X_test, y_test = load_nsl_kdd("data/KDDTest+.txt")
X_test = align_columns(X_test, X_train)

# Recover the original attack names from the raw test file
raw = pd.read_csv("data/KDDTest+.txt", header=None, names=COLUMNS)
raw["pred"] = model.predict(X_test)
raw["is_attack"] = raw["label"] != "normal"

attacks = raw[raw["is_attack"]]
per_type = attacks.groupby("label").agg(
    count=("pred", "size"),
    caught=("pred", "sum"),
)
per_type["recall"] = (per_type["caught"] / per_type["count"]).round(3)
print(per_type.sort_values("count", ascending=False))

seen = set(raw.loc[raw["label"].isin(
    pd.read_csv("data/KDDTrain+.txt", header=None, names=COLUMNS)["label"]
), "label"])
print("\nSeen in training, recall:", round(attacks[attacks["label"].isin(seen)]["pred"].mean(), 3))
print("Novel attacks, recall:  ", round(attacks[~attacks["label"].isin(seen)]["pred"].mean(), 3))
