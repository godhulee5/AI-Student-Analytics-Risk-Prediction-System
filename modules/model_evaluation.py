import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


def render(data_dir, model_dir):
    st.markdown("""<div class='hero'><h1>Model Evaluation & Comparison</h1><p>Research-focused comparison of the trained machine-learning models.</p></div>""", unsafe_allow_html=True)
    metrics_path = Path(model_dir) / "model_metrics.json"
    if not metrics_path.exists():
        st.warning("Model metrics are not available yet.")
        return
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    task = st.selectbox("Prediction task", ["Risk Prediction", "Grade Prediction"])
    key = "risk" if task.startswith("Risk") else "grade"
    rows = []
    for model, vals in metrics.get(key, {}).items():
        rows.append({"Model": model, **vals})
    comp = pd.DataFrame(rows)
    if comp.empty:
        st.info("No evaluation results found.")
        return
    st.subheader("Evaluation Metrics")
    st.dataframe(comp.style.format({c: "{:.3f}" for c in comp.columns if c != "Model"}), use_container_width=True, hide_index=True)
    metric = st.selectbox("Metric to visualize", ["Accuracy", "Precision_weighted", "Recall_weighted", "F1_weighted"])
    fig = px.bar(comp, x="Model", y=metric, text_auto=".3f", title=f"{metric} — {task}", range_y=[0, 1])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    selected = metrics.get("selected_models", {}).get(key, "Not available")
    st.info(f"The stored training pipeline selected **{selected}** using weighted F1 on its evaluation split. This is a model-selection record, not a guarantee of future performance.")
    st.caption("Research note: report the dataset size, train/test procedure, class distribution, and limitations alongside these metrics.")
