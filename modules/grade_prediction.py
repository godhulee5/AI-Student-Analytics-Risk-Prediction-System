import streamlit as st

from utils.data_manager import (
    load_students,
    save_prediction_history
)

from utils.ml_engine import predict_grade


def render(data_dir, model_dir):

    # ---------------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------------

    df = load_students(data_dir)

    # ---------------------------------------------------------
    # PAGE HEADER
    # ---------------------------------------------------------

    st.markdown(
        """
        <div class="hero">
            <h1>Grade Prediction</h1>
            <p>
                Interactive slider-based grade prediction using
                the trained ML pipeline.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Student Information")

    # ---------------------------------------------------------
    # STUDENT ID
    # ---------------------------------------------------------

    student_id = st.text_input(
        "Student ID",
        placeholder="Enter Student ID",
        help="Enter an ID to associate this prediction with a student."
    )

    # ---------------------------------------------------------
    # INPUT FEATURES
    # ---------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        gender = st.selectbox(
            "Gender",
            sorted(
                df["Gender"]
                .dropna()
                .astype(str)
                .unique()
            )
        )

        age = st.slider(
            "Age",
            16,
            40,
            21
        )

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
            0.0,
            100.0,
            80.0,
            step=0.5
        )

    with col2:

        study = st.slider(
            "Study Hours / Day",
            0.0,
            16.0,
            4.0,
            step=0.5
        )

        prev = st.slider(
            "Previous CGPA",
            0.0,
            4.0,
            3.0,
            step=0.01
        )

        sleep = st.slider(
            "Sleep Hours",
            0.0,
            14.0,
            7.0,
            step=0.5
        )

        social = st.slider(
            "Social Hours / Week",
            0.0,
            60.0,
            10.0,
            step=0.5
        )

    # ---------------------------------------------------------
    # PREDICTION BUTTON
    # ---------------------------------------------------------

    if st.button(
        "🎯 Predict Grade",
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

        else:

            # -------------------------------------------------
            # CREATE FEATURE DICTIONARY
            # -------------------------------------------------

            features = {

                "Gender": gender,

                "Age": age,

                "Major": major,

                "Attendance_Pct":
                    attendance,

                "Study_Hours_Per_Day":
                    study,

                "Previous_CGPA":
                    prev,

                "Sleep_Hours":
                    sleep,

                "Social_Hours_Week":
                    social
            }

            # -------------------------------------------------
            # RUN MODEL
            # -------------------------------------------------

            try:

                label, confidence = predict_grade(
                    features,
                    model_dir
                )

                # -------------------------------------------------
                # DISPLAY RESULT
                # -------------------------------------------------

                st.markdown("---")

                st.subheader(
                    "AI Prediction Result"
                )

                st.success(
                    f"🎓 Predicted Grade: **{label}**"
                )

                if confidence is not None:

                    st.metric(
                        "Model Confidence",
                        f"{confidence * 100:.1f}%"
                    )

                # -------------------------------------------------
                # SAVE PREDICTION
                # -------------------------------------------------

                save_prediction_history(

                    data_dir=data_dir,

                    prediction_type="Grade Prediction",

                    student_id=student_id.strip(),

                    features=features,

                    prediction=label,

                    confidence=confidence
                )

                st.success(
                    "✓ Prediction saved successfully."
                )

                st.info(
                    "This prediction has been added to the "
                    "AI Prediction History. You can download it "
                    "from the Reports section."
                )

            except Exception as e:

                st.error(
                    f"Prediction failed: {e}"
                )
