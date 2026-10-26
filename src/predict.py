# src/predict.py
import joblib
import pandas as pd

from src.preprocess import load_nsl_kdd, COLUMNS
from src.train import align_columns

MODEL_PATH = "models/random_forest.joblib"
FEATURES_PATH = "models/feature_columns.joblib"
TRAIN_PATH = "data/KDDTrain+.txt"

SHOW_COLS = ["protocol_type", "service", "flag", "src_bytes", "dst_bytes", "count"]


def score_file(input_path, output_path="alerts.csv", threshold=0.5):
    """Score connections in input_path and write flagged rows to output_path."""
    model = joblib.load(MODEL_PATH)
    feature_cols = joblib.load(FEATURES_PATH)

    X, _ = load_nsl_kdd(input_path, has_labels=False)
    X = X.reindex(columns=feature_cols, fill_value=0)

    # Probability that each connection is an attack
    scores = model.predict_proba(X)[:, 1]

    raw = pd.read_csv(input_path, header=None, names=COLUMNS[:41])
    raw["attack_score"] = scores.round(3)

    alerts = raw.loc[scores >= threshold, SHOW_COLS + ["attack_score"]]
    alerts = alerts.sort_values("attack_score", ascending=False)
    alerts.to_csv(output_path, index=False)

    return len(raw), len(alerts)