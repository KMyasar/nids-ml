# app.py
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.predict import score_file

st.set_page_config(page_title="NIDS Dashboard", layout="wide")
st.title("Network Intrusion Detection")
st.caption("Upload unlabeled NSL-KDD style traffic (41 columns, no label) to score connections.")

uploaded = st.file_uploader("Traffic CSV", type=["txt", "csv"])
threshold = st.slider("Alert threshold", 0.05, 0.95, 0.5, 0.05,
                      help="Lower values flag more connections: more attacks caught, more false alarms.")

if uploaded is not None:
    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "input.txt"
        output_path = Path(tmp) / "alerts.csv"
        input_path.write_bytes(uploaded.getvalue())

        try:
            total, n_alerts = score_file(str(input_path), str(output_path), threshold)
            alerts = pd.read_csv(output_path)
        except Exception as e:
            st.error(f"Could not score this file. Check that it has 41 columns and no label column. Details: {e}")
            st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Connections scored", f"{total:,}")
    col2.metric("Alerts", f"{n_alerts:,}")
    col3.metric("Alert rate", f"{n_alerts / total:.1%}" if total else "0%")

    st.subheader("Flagged connections")
    if alerts.empty:
        st.success("No connections exceeded the threshold.")
    else:
        st.dataframe(alerts, use_container_width=True)
        st.download_button(
            "Download alerts CSV",
            alerts.to_csv(index=False).encode("utf-8"),
            file_name="alerts.csv",
            mime="text/csv",
        )
else:
    st.info("Upload a file to begin.")