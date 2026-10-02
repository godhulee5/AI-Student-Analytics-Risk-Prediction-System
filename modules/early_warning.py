import streamlit as st
import pandas as pd

from utils.data_manager import (
    load_students,
    load_prediction_history,
    load_interventions
)


def render(data_dir, model_dir):

    df = load_students(data_dir)
    history = load_prediction_history(data_dir)
    interventions = load_interventions(data_dir)

    st.markdown(
        """
        <div class="hero">
            <h1>Early Warning System</h1>
            <p>
                Monitor existing high-risk students and newly detected
                high-risk students from AI risk predictions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # EXISTING HIGH-RISK STUDENTS
    # ---------------------------------------------------------

    high = df[
        df["Risk_Level"].astype(str).str.strip().eq("High Risk")
    ].copy()

    # ---------------------------------------------------------
    # NEW HIGH-RISK AI PREDICTIONS
    # ---------------------------------------------------------

    new_alerts = pd.DataFrame()

    if not history.empty and "Prediction_Type" in history.columns:
        new_alerts = history[
            history["Prediction_Type"].astype(str).eq("Risk Prediction")
            & history["Prediction"].astype(str).str.strip().eq("High Risk")
        ].copy()

        if not new_alerts.empty:
            # Keep only the latest prediction for each student.
            new_alerts["Prediction_Date_Time"] = pd.to_datetime(
                new_alerts["Prediction_Date_Time"],
                errors="coerce"
            )
            new_alerts = (
                new_alerts
                .sort_values("Prediction_Date_Time")
                .drop_duplicates(
                    subset=["Student_ID"],
                    keep="last"
                )
            )

    # ---------------------------------------------------------
    # MERGE DATASET ALERTS + NEW AI ALERTS
    # ---------------------------------------------------------

    existing_ids = set(
        high["Student_ID"].astype(str).str.strip()
    ) if "Student_ID" in high.columns else set()

    if not new_alerts.empty:
        # Only add AI alerts that are not already present
        # in the existing High Risk dataset.
        new_alerts = new_alerts[
            ~new_alerts["Student_ID"]
            .astype(str)
            .str.strip()
            .isin(existing_ids)
        ].copy()

    open_cases = 0
    if not interventions.empty and "Status" in interventions.columns:
        open_cases = int(interventions["Status"].astype(str).isin(["Open", "In Progress"]).sum())

    c1, c2, c3 = st.columns(3)

    c1.metric("High Risk", len(high))
    c2.metric("New AI Alerts", len(new_alerts))
    c3.metric("Total Alerts", len(high) + len(new_alerts))
    st.metric("Open / In-Progress Interventions", open_cases)

    # ---------------------------------------------------------
    # NEW AI ALERTS
    # ---------------------------------------------------------

    st.subheader("🆕 Newly Predicted High-Risk Students")

    if new_alerts.empty:
        st.success("No new High Risk AI predictions require an alert.")
    else:
        alert_columns = [
            "Student_ID",
            "Major",
            "Attendance_Pct",
            "Previous_CGPA",
            "Study_Hours_Per_Day",
            "Sleep_Hours",
            "Social_Hours_Week",
            "Prediction",
            "Confidence",
            "Prediction_Date_Time"
        ]

        available = [
            c for c in alert_columns
            if c in new_alerts.columns
        ]

        display_new = new_alerts[available].copy()

        if "Confidence" in display_new.columns:
            display_new["Confidence"] = pd.to_numeric(
                display_new["Confidence"],
                errors="coerce"
            ).map(
                lambda x: f"{x:.1f}%" if pd.notna(x) else ""
            )

        st.dataframe(
            display_new,
            use_container_width=True,
            hide_index=True
        )

    # ---------------------------------------------------------
    # ALL HIGH-RISK STUDENTS
    # ---------------------------------------------------------

    st.subheader("🚨 High-Risk Students")

    if high.empty and new_alerts.empty:
        st.success("No high-risk alerts in the current system.")
        return

    display_columns = [
        "Student_ID",
        "Major",
        "Attendance_Pct",
        "Previous_CGPA",
        "Study_Hours_Per_Day",
        "Final_CGPA",
        "Risk_Level"
    ]

    available = [
        c for c in display_columns
        if c in high.columns
    ]

    display = high[available].copy()

    if not new_alerts.empty:
        new_rows = pd.DataFrame({
            "Student_ID": new_alerts["Student_ID"].astype(str),
            "Major": new_alerts.get("Major", ""),
            "Attendance_Pct": new_alerts.get("Attendance_Pct", ""),
            "Previous_CGPA": new_alerts.get("Previous_CGPA", ""),
            "Study_Hours_Per_Day": new_alerts.get("Study_Hours_Per_Day", ""),
            "Final_CGPA": "",
            "Risk_Level": "High Risk"
        })

        new_rows = new_rows[display_columns]
        display = pd.concat(
            [display, new_rows],
            ignore_index=True
        )

    display = display.drop_duplicates(
        subset=["Student_ID"],
        keep="first"
    )

    display = display.sort_values(
        ["Attendance_Pct", "Previous_CGPA"],
        na_position="last"
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    csv = display.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download High-Risk Alert List",
        csv,
        "high_risk_students.csv",
        "text/csv"
    )

    st.subheader("Intervention Status")
    if interventions.empty:
        st.info("No intervention records yet. Use Intervention Management to record follow-up actions.")
    else:
        st.dataframe(interventions.sort_values("Created_At", ascending=False).head(10), use_container_width=True, hide_index=True)

    st.subheader("Suggested administrative workflow")

    st.markdown(
        """
        1. Review the student's attendance and academic indicators.
        2. Contact the relevant academic mentor.
        3. Record an intervention or counselling action.
        4. Reassess the student after updated data is entered.
        5. Keep human review in the decision process.
        """
    )
