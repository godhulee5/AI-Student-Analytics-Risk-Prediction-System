import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_manager import load_students


def metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render(data_dir, model_dir):

    # --------------------------------------------------
    # LOAD STUDENT DATA
    # --------------------------------------------------

    df = load_students(data_dir)

    # --------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # --------------------------------------------------

    required_columns = [
        "Final_CGPA",
        "Attendance_Pct",
        "Risk_Level"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        st.error(
            "The current student dataset is missing required columns."
        )

        st.write("Missing columns:")

        for column in missing_columns:
            st.write(f"- `{column}`")

        st.info(
            "Please restore/upload the correct "
            "`student_data_cleaned.csv` generated for this project."
        )

        st.write("Current dataset columns:")

        st.code(
            "\n".join(df.columns.astype(str))
        )

        return

    # --------------------------------------------------
    # DASHBOARD FILTERS
    # --------------------------------------------------
    with st.expander("🔎 Dashboard Filters", expanded=False):
        selected_major = st.multiselect("Major", sorted(df["Major"].dropna().astype(str).unique())) if "Major" in df.columns else []
        selected_risk = st.multiselect("Risk Level", sorted(df["Risk_Level"].dropna().astype(str).unique()))
        view_df = df.copy()
        if selected_major:
            view_df = view_df[view_df["Major"].astype(str).isin(selected_major)]
        if selected_risk:
            view_df = view_df[view_df["Risk_Level"].astype(str).isin(selected_risk)]
    if 'view_df' not in locals():
        view_df = df

    # --------------------------------------------------
    # HERO SECTION
    # --------------------------------------------------

    st.markdown(
        """
        <div class="hero">
            <h1>College Student Intelligence</h1>
            <p>
                Real-time academic monitoring, AI-assisted risk detection
                and grade forecasting for administrators.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # TOP METRICS
    # --------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric(
            "Total Students",
            f"{len(view_df):,}"
        )

    with c2:
        metric(
            "Average CGPA",
            f"{view_df['Final_CGPA'].mean():.2f}"
        )

    with c3:
        metric(
            "Average Attendance",
            f"{view_df['Attendance_Pct'].mean():.1f}%"
        )

    with c4:
        high_risk = (
            view_df["Risk_Level"]
            .astype(str)
            .str.strip()
            .eq("High Risk")
            .sum()
        )

        metric(
            "High Risk Students",
            f"{high_risk:,}"
        )

    # --------------------------------------------------
    # ACADEMIC OVERVIEW
    # --------------------------------------------------

    st.markdown(
        "<div class='section-title'>Academic Overview</div>",
        unsafe_allow_html=True
    )

    a, b = st.columns(2)

    # --------------------------------------------------
    # CGPA DISTRIBUTION
    # --------------------------------------------------

    with a:

        fig = px.histogram(
            view_df,
            x="Final_CGPA",
            nbins=18,
            title="CGPA Distribution"
        )

        fig.update_layout(
            height=350,
            margin=dict(
                l=20,
                r=20,
                t=55,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------

    with b:

        rc = (
            view_df["Risk_Level"]
            .value_counts()
            .reset_index()
        )

        rc.columns = [
            "Risk_Level",
            "Students"
        ]

        fig = px.pie(
            rc,
            names="Risk_Level",
            values="Students",
            hole=0.55,
            title="Academic Risk Distribution"
        )

        fig.update_layout(
            height=350,
            margin=dict(
                l=20,
                r=20,
                t=55,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------
    # ATTENDANCE VS CGPA
    # --------------------------------------------------

    st.markdown(
        "<div class='section-title'>Attendance vs CGPA</div>",
        unsafe_allow_html=True
    )

    hover_columns = [
        column
        for column in [
            "Student_ID",
            "Major",
            "Previous_CGPA"
        ]
        if column in df.columns
    ]

    fig = px.scatter(
        view_df,
        x="Attendance_Pct",
        y="Final_CGPA",
        color="Risk_Level",
        hover_data=hover_columns,
        title="Attendance and Final CGPA"
    )

    fig.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    st.caption(
        "Data shown from the current student dataset. "
        "AI outputs are decision-support indicators."
    )