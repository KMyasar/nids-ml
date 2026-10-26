# src/preprocess.py
import pandas as pd

COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label", "difficulty",
]

CATEGORICAL = ["protocol_type", "service", "flag"]


def load_nsl_kdd(path):
    """Load an NSL-KDD file and return features X and binary labels y."""
    df = pd.read_csv(path, header=None, names=COLUMNS)
    df = df.drop(columns=["difficulty"])

    # 0 = normal traffic, 1 = any attack
    y = (df["label"] != "normal").astype(int)
    X = df.drop(columns=["label"])

    # One-hot encode the text columns; numeric columns pass through
    X = pd.get_dummies(X, columns=CATEGORICAL)
    return X, y


if __name__ == "__main__":
    X, y = load_nsl_kdd("data/KDDTrain+.txt")
    print("Features shape:", X.shape)
    print("Attack rate:", round(y.mean(), 3))
    print("Class counts:\n", y.value_counts())
