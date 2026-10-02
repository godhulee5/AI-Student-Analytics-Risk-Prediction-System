import streamlit as st
import plotly.express as px

from utils.data_manager import load_students


def render(data_dir, model_dir):

    df = load_students(data_dir)

    st.markdown(
        """
        <div class="hero">
            <h1>Academic Analytics</h1>
            <p>
                Explore performance patterns by attendance,
                study habits, major and prior achievement.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # ---------------------------------------------------------

    required_columns = [
        "Major",
        "Gender",
        "Study_Hours_Per_Day",
        "Final_CGPA",
        "Attendance_Pct",
        "Previous_CGPA"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        st.error(
            "The dataset is missing the following columns: "
            + ", ".join(missing)
        )

        st.write("Available columns:")
        st.write(list(df.columns))

        return

    # ---------------------------------------------------------
    # FILTERS
    # ---------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    majors = sorted(
        df["Major"].dropna().astype(str).unique()
    )

    genders = sorted(
        df["Gender"].dropna().astype(str).unique()
    )

    major = c1.multiselect(
        "Major",
        majors,
        default=majors
    )

    gender = c2.multiselect(
        "Gender",
        genders,
        default=genders
    )

    # ---------------------------------------------------------
    # RISK FILTER
    # ---------------------------------------------------------

    has_risk = "Risk_Level" in df.columns

    if has_risk:

        risks = sorted(
            df["Risk_Level"]
            .dropna()
            .astype(str)
            .unique()
        )

        risk = c3.multiselect(
            "Risk Level",
            risks,
            default=risks
        )

        view = df[
            df["Major"].astype(str).isin(major)
            & df["Gender"].astype(str).isin(gender)
            & df["Risk_Level"].astype(str).isin(risk)
        ].copy()

    else:

        c3.info(
            "Risk Level is not available in the current dataset."
        )

        view = df[
            df["Major"].astype(str).isin(major)
            & df["Gender"].astype(str).isin(gender)
        ].copy()

    # ---------------------------------------------------------
    # NO DATA CHECK
    # ---------------------------------------------------------

    if view.empty:

        st.warning(
            "No students match the selected filters."
        )

        return

    # ---------------------------------------------------------
    # SUMMARY METRICS
    # ---------------------------------------------------------

    st.markdown(
        "<div class='section-title'>Analytics Summary</div>",
        unsafe_allow_html=True
    )

    m1, m2, m3, m4 = st.columns(4)

    avg_cgpa = view["Final_CGPA"].mean()
    avg_attendance = view["Attendance_Pct"].mean()
    avg_study = view["Study_Hours_Per_Day"].mean()

    m1.metric(
        "Students",
        f"{len(view):,}"
    )

    m2.metric(
        "Average CGPA",
        f"{avg_cgpa:.2f}"
    )

    m3.metric(
        "Average Attendance",
        f"{avg_attendance:.1f}%"
    )

    m4.metric(
        "Average Study Hours",
        f"{avg_study:.1f}"
    )

    # ---------------------------------------------------------
    # STUDY HOURS VS CGPA
    # ---------------------------------------------------------

    a, b = st.columns(2)

    with a:

        if has_risk:

            fig = px.scatter(
                view,
                x="Study_Hours_Per_Day",
                y="Final_CGPA",
                color="Risk_Level",
                hover_data=[
                    col for col in [
                        "Student_ID",
                        "Major"
                    ]
                    if col in view.columns
                ],
                title="Study Hours vs Final CGPA"
            )

        else:

            fig = px.scatter(
                view,
                x="Study_Hours_Per_Day",
                y="Final_CGPA",
                hover_data=[
                    col for col in [
                        "Student_ID",
                        "Major"
                    ]
                    if col in view.columns
                ],
                title="Study Hours vs Final CGPA"
            )

        fig.update_layout(
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # AVERAGE CGPA BY MAJOR
    # ---------------------------------------------------------

    with b:

        agg = (
            view
            .groupby("Major", as_index=False)
            .agg(
                Average_CGPA=("Final_CGPA", "mean"),
                Average_Attendance=(
                    "Attendance_Pct",
                    "mean"
                )
            )
        )

        fig = px.bar(
            agg,
            x="Major",
            y="Average_CGPA",
            title="Average CGPA by Major",
            text_auto=".2f"
        )

        fig.update_layout(
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # PREVIOUS CGPA VS FINAL CGPA
    # ---------------------------------------------------------

    a, b = st.columns(2)

    with a:

        fig = px.scatter(
            view,
            x="Previous_CGPA",
            y="Final_CGPA",
            color="Major",
            hover_data=[
                col for col in [
                    "Student_ID",
                    "Gender"
                ]
                if col in view.columns
            ],
            title="Previous CGPA vs Final CGPA"
        )

        fig.update_layout(
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # ATTENDANCE BY MAJOR
    # ---------------------------------------------------------

    with b:

        fig = px.box(
            view,
            x="Major",
            y="Attendance_Pct",
            title="Attendance by Major"
        )

        fig.update_layout(
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # RISK ANALYSIS
    # ---------------------------------------------------------

    if has_risk:

        st.markdown(
            "<div class='section-title'>Risk Analysis</div>",
            unsafe_allow_html=True
        )

        risk_summary = (
            view["Risk_Level"]
            .value_counts()
            .reset_index()
        )

        risk_summary.columns = [
            "Risk_Level",
            "Students"
        ]

        fig = px.bar(
            risk_summary,
            x="Risk_Level",
            y="Students",
            title="Student Risk Distribution",
            text="Students"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Risk analysis will become available when "
            "Risk_Level prediction results are stored "
            "in the student/prediction data."
        )

    # ---------------------------------------------------------
    # DATA TABLE
    # ---------------------------------------------------------

    st.markdown(
        "<div class='section-title'>Filtered Student Data</div>",
        unsafe_allow_html=True
    )

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True
    )