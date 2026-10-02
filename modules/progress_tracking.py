import pandas as pd
import plotly.express as px
import streamlit as st
from utils.data_manager import load_students, load_prediction_history


def render(data_dir, model_dir):
    df = load_students(data_dir)
    history = load_prediction_history(data_dir)
    st.markdown("""<div class='hero'><h1>Student Progress Tracking</h1><p>Track academic indicators and changes in AI risk predictions over time.</p></div>""", unsafe_allow_html=True)
    ids = sorted(df["Student_ID"].astype(str).unique()) if "Student_ID" in df.columns else []
    if not ids:
        st.warning("No student IDs available.")
        return
    sid = st.selectbox("Select Student", ids)
    row = df[df["Student_ID"].astype(str) == sid].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Attendance", f"{float(row['Attendance_Pct']):.1f}%")
    c2.metric("Previous CGPA", f"{float(row['Previous_CGPA']):.2f}")
    c3.metric("Final CGPA", f"{float(row['Final_CGPA']):.2f}")
    c4.metric("Current Dataset Risk", str(row["Risk_Level"]))
    left, right = st.columns(2)
    with left:
        vals = pd.DataFrame({"Indicator":["Attendance %", "Previous CGPA", "Final CGPA"], "Value":[float(row["Attendance_Pct"]), float(row["Previous_CGPA"])*25, float(row["Final_CGPA"])*25]})
        fig = px.bar(vals, x="Indicator", y="Value", title="Academic Indicators (CGPA scaled ×25)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Risk Prediction History")
        if history.empty or "Student_ID" not in history.columns:
            st.info("No prediction history available.")
        else:
            h = history[(history["Student_ID"].astype(str) == sid) & (history["Prediction_Type"].astype(str) == "Risk Prediction")].copy()
            if h.empty:
                st.info("No AI risk predictions recorded for this student.")
            else:
                h["Prediction_Date_Time"] = pd.to_datetime(h["Prediction_Date_Time"], errors="coerce")
                h["Risk_Code"] = h["Prediction"].map({"Low Risk":1,"Medium Risk":2,"High Risk":3}).fillna(0)
                fig = px.line(h.sort_values("Prediction_Date_Time"), x="Prediction_Date_Time", y="Risk_Code", markers=True, title="Risk Level Over Time")
                fig.update_yaxes(tickmode="array", tickvals=[1,2,3], ticktext=["Low Risk","Medium Risk","High Risk"], range=[0.5,3.5])
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(h[[c for c in ["Prediction_Date_Time","Prediction","Confidence","Attendance_Pct","Previous_CGPA"] if c in h.columns]].sort_values("Prediction_Date_Time", ascending=False), use_container_width=True, hide_index=True)
    st.subheader("Student Profile")
    st.dataframe(pd.DataFrame([row]), use_container_width=True, hide_index=True)
