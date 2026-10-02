```python
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from utils.data_manager import (
    load_students,
    save_prediction_history,
)
from utils.ml_engine import predict_risk


def render(data_dir, model_dir):

    # Load student dataset
    df = load_students(data_dir)

    # ---------------------------------------------------------
    # HERO SECTION
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="hero">
            <h1>AI Risk Prediction</h1>
            <p>
                Predict a student's academic risk level using the trained
                machine-learning model. New High Risk predictions are
                automatically added to the Early Warning System.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # STUDENT INFORMATION
    # ---------------------------------------------------------
    st.subheader("Student Information")

    student_id = st.text_input(
        "Student ID",
        placeholder="Enter Student ID",
        help="Enter the Student ID so the prediction can be tracked in the Early Warning System."
    )

    col1, col2 = st.columns(2)

    # ---------------------------------------------------------
    # LEFT COLUMN
    # ---------------------------------------------------------
    with col1:

        major = st.selectbox(
            "Major",
            sorted(
                df["Major"]
                .dropna()
                .astype(str)
                .unique()
            )
        )

        attendance = st.slider(
            "Attendance %",
            min_value=0.0,
            max_value=100.0,
            value=80.0,
            step=0.5
        )

        prev = st.slider(
            "Previous CGPA",
            min_value=0.0,
            max_value=4.0,
            value=3.0,
            step=0.01
        )

    # ---------------------------------------------------------
    # RIGHT COLUMN
    # ---------------------------------------------------------
    with col2:

        study = st.slider(
            "Study Hours / Day",
            min_value=0.0,
            max_value=16.0,
            value=4.0,
            step=0.5
        )

        sleep = st.slider(
            "Sleep Hours",
            min_value=0.0,
            max_value=14.0,
            value=7.0,
            step=0.5
        )

        social = st.slider(
            "Social Hours / Week",
            min_value=0.0,
            max_value=60.0,
            value=10.0,
            step=0.5
        )

    # ---------------------------------------------------------
    # PREDICT BUTTON
    # ---------------------------------------------------------
    if st.button(
        "⚠️ Predict Risk",
        type="primary",
        use_container_width=True
    ):

        # -----------------------------------------------------
        # VALIDATE STUDENT ID
        # -----------------------------------------------------
        if not student_id.strip():

            st.error(
                "Please enter a Student ID before making a prediction."
            )

            return

        # -----------------------------------------------------
        # CREATE MODEL INPUT
        # -----------------------------------------------------
        features = {
            "Major": major,
            "Attendance_Pct": attendance,
            "Previous_CGPA": prev,
            "Study_Hours_Per_Day": study,
            "Sleep_Hours": sleep,
            "Social_Hours_Week": social
        }

        # -----------------------------------------------------
        # MODEL PREDICTION
        # -----------------------------------------------------
        try:

            label, confidence = predict_risk(
                features,
                model_dir
            )

            # -------------------------------------------------
            # RESULT
            # -------------------------------------------------
            st.markdown("---")

            st.subheader(
                "AI Risk Prediction Result"
            )

            # -------------------------------------------------
            # DISPLAY RISK LEVEL
            # -------------------------------------------------
            if label == "High Risk":

                st.error(
                    f"🚨 Predicted Risk Level: **{label}**"
                )

            elif label == "Medium Risk":

                st.warning(
                    f"⚠️ Predicted Risk Level: **{label}**"
                )

            else:

                st.success(
                    f"✅ Predicted Risk Level: **{label}**"
                )

            # -------------------------------------------------
            # MODEL CONFIDENCE
            # -------------------------------------------------
            if confidence is not None:

                st.metric(
                    "Model Confidence",
                    f"{confidence * 100:.1f}%"
                )

            # -------------------------------------------------
            # SAVE PREDICTION HISTORY
            # -------------------------------------------------
            save_prediction_history(
                data_dir=data_dir,
                prediction_type="Risk Prediction",
                student_id=student_id.strip(),
                features=features,
                prediction=label,
                confidence=confidence
            )

            # -------------------------------------------------
            # EXPLAINABLE AI
            # -------------------------------------------------
            st.markdown("---")

            st.subheader(
                "🔎 Explainable AI — Prediction Factors"
            )

            importance_path = (
                Path(model_dir)
                / "risk_feature_importance.csv"
            )

            if importance_path.exists():

                imp = pd.read_csv(
                    importance_path
                )

                # Clean feature names
                imp["Feature_Display"] = (
                    imp["Feature"]
                    .astype(str)
                    .str.replace(
                        "num__",
                        "",
                        regex=False
                    )
                    .str.replace(
                        "cat__",
                        "",
                        regex=False
                    )
                    .str.replace(
                        "_",
                        " ",
                        regex=False
                    )
                )

                # Select strongest features
                imp = (
                    imp
                    .sort_values(
                        "Importance",
                        ascending=False
                    )
                    .head(8)
                )

                # Create chart
                chart_data = (
                    imp
                    .sort_values("Importance")
                )

                fig = px.bar(
                    chart_data,
                    x="Importance",
                    y="Feature_Display",
                    orientation="h",
                    title="Stored Global Feature Importance"
                )

                fig.update_layout(
                    height=350,
                    yaxis_title="Feature",
                    xaxis_title="Importance"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key="risk_feature_importance_chart"
                )

                st.caption(
                    "These are global model feature-importance values, "
                    "not proof that any single factor caused this student's "
                    "prediction."
                )

            else:

                st.info(
                    "Feature-importance file is not available."
                )

            # -------------------------------------------------
            # EARLY WARNING SYSTEM
            # -------------------------------------------------
            if label == "High Risk":

                st.success(
                    f"✓ {student_id.strip()} has been automatically "
                    "added to the Early Warning System."
                )

                st.info(
                    "Open **Early Warning System** to view the new alert."
                )

            else:

                st.success(
                    "✓ Risk prediction saved successfully."
                )

        # -----------------------------------------------------
        # ERROR HANDLING
        # -----------------------------------------------------
        except Exception as e:

            st.error(
                f"Risk prediction failed: {e}"
            )
```
