# src/cli.py
from src import __version__
import argparse

from sklearn.metrics import classification_report, confusion_matrix

from src.predict import score_file, MODEL_PATH, FEATURES_PATH
from src.preprocess import load_nsl_kdd
from src.train import align_columns
import joblib


def cmd_predict(args):
    total, alerts = score_file(args.input, args.output, args.threshold)
    print(f"Scored {total} connections. {alerts} alerts written to {args.output}")


def cmd_report(args):
    model = joblib.load(MODEL_PATH)
    feature_cols = joblib.load(FEATURES_PATH)
    X_test, y_test = load_nsl_kdd(args.test)
    X_test = X_test.reindex(columns=feature_cols, fill_value=0)
    preds = model.predict(X_test)
    print(classification_report(y_test, preds, target_names=["normal", "attack"], digits=3))
    print("Confusion matrix (rows = actual, cols = predicted):")
    print(confusion_matrix(y_test, preds))


def main():
    parser = argparse.ArgumentParser(prog="ids", description="Network intrusion detector")
    parser.add_argument("--version", action="version", version=f"ids {__version__}")
    parser.add_argument("-v",action="version", version=f"ids {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("predict", help="Score traffic and write alerts to CSV")
    p.add_argument("--input", required=True, help="NSL-KDD formatted file")
    p.add_argument("--output", default="alerts.csv")
    p.add_argument("--threshold", type=float, default=0.5,
                   help="Attack probability cutoff (lower = more alerts)")
    p.set_defaults(func=cmd_predict)

    r = sub.add_parser("report", help="Show model metrics on a labeled test file")
    r.add_argument("--test", default="data/KDDTest+.txt")
    r.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
