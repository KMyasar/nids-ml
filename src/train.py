# src/train.py
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

from src.preprocess import load_nsl_kdd

MODEL_DIR = Path("models")


def align_columns(X_test, X_train):
    """Make test features match training features exactly."""
    return X_test.reindex(columns=X_train.columns, fill_value=0)


def evaluate(name, model, X_test, y_test):
    preds = model.predict(X_test)
    print(f"\n=== {name} ===")
    print(classification_report(y_test, preds, target_names=["normal", "attack"], digits=3))
    print("Confusion matrix (rows = actual, cols = predicted):")
    print(confusion_matrix(y_test, preds))


def main():
    MODEL_DIR.mkdir(exist_ok=True)

    X_train, y_train = load_nsl_kdd("data/KDDTrain+.txt")
    X_test, y_test = load_nsl_kdd("data/KDDTest+.txt")
    X_test = align_columns(X_test, X_train)

    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"Test attack rate: {y_test.mean():.3f}")

    # Baseline: Logistic Regression needs scaled inputs
    baseline = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    baseline.fit(X_train, y_train)
    evaluate("Logistic Regression (baseline)", baseline, X_test, y_test)

    # Stronger model: Random Forest handles raw features well
    forest = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42, class_weight="balanced")
    forest.fit(X_train, y_train)
    evaluate("Random Forest", forest, X_test, y_test)

    joblib.dump(forest, MODEL_DIR / "random_forest.joblib")
    joblib.dump(list(X_train.columns), MODEL_DIR / "feature_columns.joblib")
    print("\nSaved models/random_forest.joblib and feature_columns.joblib")


if __name__ == "__main__":
    main()
