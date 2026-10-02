import streamlit as st
import pandas as pd

from utils.data_manager import (
    load_students,
    load_prediction_history
)


def render(data_dir, model_dir):

    # ---------------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------------

    df = load_students(data_dir)

    history = load_prediction_history(
        data_dir
    )

    # ---------------------------------------------------------
    # PAGE HEADER
    # ---------------------------------------------------------

    st.markdown(
        """
        <div class="hero">
            <h1>Reports</h1>
            <p>
                Download student academic data, AI predictions
                and early-warning reports.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # REPORT TABS
    # ---------------------------------------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "📊 Student Analytics",
            "🤖 AI Prediction History",
            "⚠️ Risk Report"
        ]
    )

    # =========================================================
    # TAB 1 — STUDENT ANALYTICS
    # =========================================================

    with tab1:

        st.subheader(
            "Student Analytics Export"
        )

        st.write(
            f"Total student records: **{len(df)}**"
        )

        # Display current student data
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # Convert to CSV
        csv = df.to_csv(
            index=False
        ).encode("utf-8")

        # Download
        st.download_button(
            label="⬇️ Download Student CSV",
            data=csv,
            file_name="student_analytics_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    # =========================================================
    # TAB 2 — AI PREDICTION HISTORY
    # =========================================================

    with tab2:

        st.subheader(
            "AI Prediction History"
        )

        # -----------------------------------------------------
        # CHECK WHETHER PREDICTIONS EXIST
        # -----------------------------------------------------

        if history.empty:

            st.info(
                "No AI predictions have been saved yet. "
                "Make a Grade Prediction or Risk Prediction "
                "first."
            )

        else:

            # -------------------------------------------------
            # SUMMARY
            # -------------------------------------------------

            total_predictions = len(
                history
            )

            grade_count = len(
                history[
                    history["Prediction_Type"]
                    == "Grade Prediction"
                ]
            )

            risk_count = len(
                history[
                    history["Prediction_Type"]
                    == "Risk Prediction"
                ]
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Total Predictions",
                total_predictions
            )

            c2.metric(
                "Grade Predictions",
                grade_count
            )

            c3.metric(
                "Risk Predictions",
                risk_count
            )

            st.markdown("---")

            # -------------------------------------------------
            # FILTER
            # -------------------------------------------------

            prediction_filter = st.selectbox(
                "Filter Prediction Type",
                [
                    "All Predictions",
                    "Grade Prediction",
                    "Risk Prediction"
                ]
            )

            display_history = history.copy()

            if prediction_filter != "All Predictions":

                display_history = display_history[
                    display_history[
                        "Prediction_Type"
                    ]
                    == prediction_filter
                ]

            # -------------------------------------------------
            # SEARCH STUDENT
            # -------------------------------------------------

            search_student = st.text_input(
                "Search Student ID",
                placeholder="Example: STU1001"
            )

            if search_student:

                display_history = display_history[
                    display_history[
                        "Student_ID"
                    ]
                    .astype(str)
                    .str.contains(
                        search_student,
                        case=False,
                        na=False
                    )
                ]

            # -------------------------------------------------
            # DISPLAY HISTORY
            # -------------------------------------------------

            st.write(
                f"Showing **{len(display_history)}** prediction(s)"
            )

            st.dataframe(
                display_history,
                use_container_width=True,
                hide_index=True
            )

            # -------------------------------------------------
            # DOWNLOAD ALL/FILTERED PREDICTIONS
            # -------------------------------------------------

            prediction_csv = (
                display_history
                .to_csv(
                    index=False
                )
                .encode("utf-8")
            )

            st.download_button(
                label="⬇️ Download Prediction History",
                data=prediction_csv,
                file_name="ai_prediction_history.csv",
                mime="text/csv",
                use_container_width=True
            )

    # =========================================================
    # TAB 3 — RISK REPORT
    # =========================================================

    with tab3:

        st.subheader(
            "High-Risk Student Report"
        )

        # Find high-risk students
        if "Risk_Level" in df.columns:

            high_risk = df[
                df["Risk_Level"]
                .astype(str)
                .str.lower()
                .eq("high risk")
            ].copy()

        else:

            high_risk = pd.DataFrame()

        # -----------------------------------------------------
        # NO HIGH-RISK STUDENTS
        # -----------------------------------------------------

        if high_risk.empty:

            st.success(
                "No high-risk students found in the current dataset."
            )

        else:

            st.warning(
                f"{len(high_risk)} high-risk student(s) "
                "require administrative attention."
            )

            # -------------------------------------------------
            # SELECT REPORT COLUMNS
            # -------------------------------------------------

            columns = [
                "Student_ID",
                "Gender",
                "Age",
                "Major",
                "Attendance_Pct",
                "Study_Hours_Per_Day",
                "Previous_CGPA",
                "Final_CGPA",
                "Grade",
                "Risk_Level"
            ]

            available_columns = [
                column
                for column in columns
                if column in high_risk.columns
            ]

            # -------------------------------------------------
            # DISPLAY
            # -------------------------------------------------

            st.dataframe(
                high_risk[
                    available_columns
                ],
                use_container_width=True,
                hide_index=True
            )

            # -------------------------------------------------
            # DOWNLOAD
            # -------------------------------------------------

            risk_csv = (
                high_risk[
                    available_columns
                ]
                .to_csv(
                    index=False
                )
                .encode("utf-8")
            )

            st.download_button(
                label="⬇️ Download High-Risk Report",
                data=risk_csv,
                file_name="high_risk_students.csv",
                mime="text/csv",
                use_container_width=True
            )
