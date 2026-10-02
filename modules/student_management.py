
import streamlit as st
import pandas as pd

from utils.data_manager import (
    load_students,
    save_students,
    grade_from_cgpa,
    risk_from_row
)


def invalidate_models(model_dir):
    """
    Delete old ML model files after student data is changed.
    The application will retrain the models automatically.
    """

    model_files = [
        "grade_model.pkl",
        "risk_model.pkl",
        "grade_encoder.pkl",
        "risk_encoder.pkl",
        "model_metrics.json"
    ]

    for filename in model_files:
        file_path = model_dir / filename

        if file_path.exists():
            file_path.unlink()


def render(data_dir, model_dir):

    # ---------------------------------------------------------
    # PAGE HEADER
    # ---------------------------------------------------------

    st.markdown(
        """
        <div class="hero">
            <h1>Student Management</h1>
            <p>
                Create, view, update and delete college student records.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Load current student data
    df = load_students(data_dir)

    # ---------------------------------------------------------
    # SUMMARY CARDS
    # ---------------------------------------------------------

    total_students = len(df)
    total_male = len(df[df["Gender"].astype(str).str.lower() == "male"])
    total_female = len(df[df["Gender"].astype(str).str.lower() == "female"])
    total_high_risk = len(df[df["Risk_Level"] == "High Risk"])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Students",
        total_students
    )

    c2.metric(
        "Male Students",
        total_male
    )

    c3.metric(
        "Female Students",
        total_female
    )

    c4.metric(
        "High Risk",
        total_high_risk
    )

    st.markdown("---")

    # ---------------------------------------------------------
    # CRUD TABS
    # ---------------------------------------------------------

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📋 Student Directory",
            "➕ Add Student",
            "✏️ Update Student",
            "🗑️ Delete Student"
        ]
    )

    # =========================================================
    # READ
    # =========================================================

    with tab1:

        st.subheader("Student Directory")

        col1, col2, col3 = st.columns(3)

        with col1:
            search = st.text_input(
                "Search",
                placeholder="Student ID, name or major..."
            )

        with col2:
            major_filter = st.selectbox(
                "Major",
                ["All"] + sorted(
                    df["Major"].dropna().astype(str).unique().tolist()
                )
            )

        with col3:
            risk_filter = st.selectbox(
                "Risk Level",
                ["All", "Low Risk", "Medium Risk", "High Risk"]
            )

        # Copy dataframe
        view = df.copy()

        # Search
        if search:

            mask = view.astype(str).apply(
                lambda column: column.str.contains(
                    search,
                    case=False,
                    na=False
                )
            ).any(axis=1)

            view = view[mask]

        # Major filter
        if major_filter != "All":

            view = view[
                view["Major"].astype(str) == major_filter
            ]

        # Risk filter
        if risk_filter != "All":

            view = view[
                view["Risk_Level"] == risk_filter
            ]

        st.write(
            f"Showing **{len(view)}** student(s)"
        )

        # Select useful columns for display
        display_columns = [
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
            for column in display_columns
            if column in view.columns
        ]

        st.dataframe(
            view[available_columns],
            use_container_width=True,
            hide_index=True
        )

        # Download current filtered records
        csv = view.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download Student Records",
            csv,
            "student_records.csv",
            "text/csv"
        )

    # =========================================================
    # CREATE
    # =========================================================

    with tab2:

        st.subheader("Add New Student")

        with st.form("add_student_form"):

            st.markdown("### Student Information")

            c1, c2, c3 = st.columns(3)

            with c1:

                sid = st.text_input(
                    "Student ID *",
                    placeholder="Example: STU1001"
                )

            with c2:

                gender = st.selectbox(
                    "Gender",
                    sorted(
                        df["Gender"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )
                )

            with c3:

                age = st.number_input(
                    "Age",
                    min_value=15,
                    max_value=60,
                    value=20
                )

            major = st.selectbox(
                "Major",
                sorted(
                    df["Major"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
            )

            st.markdown("### Academic & Lifestyle Information")

            c1, c2 = st.columns(2)

            with c1:

                attendance = st.slider(
                    "Attendance (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=80.0,
                    step=0.5
                )

                study = st.slider(
                    "Study Hours / Day",
                    min_value=0.0,
                    max_value=16.0,
                    value=4.0,
                    step=0.5
                )

                previous_cgpa = st.slider(
                    "Previous CGPA",
                    min_value=0.0,
                    max_value=4.0,
                    value=3.0,
                    step=0.01
                )

            with c2:

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

                final_cgpa = st.slider(
                    "Final CGPA",
                    min_value=0.0,
                    max_value=4.0,
                    value=3.0,
                    step=0.01
                )

            submitted = st.form_submit_button(
                "➕ Add Student",
                use_container_width=True
            )

            if submitted:

                # Check Student ID
                if not sid.strip():

                    st.error(
                        "Student ID is required."
                    )

                elif sid.strip() in df["Student_ID"].astype(str).values:

                    st.error(
                        "This Student ID already exists."
                    )

                else:

                    # Create new student
                    new_student = pd.DataFrame(
                        [
                            {
                                "Student_ID": sid.strip(),
                                "Gender": gender,
                                "Age": age,
                                "Major": major,
                                "Attendance_Pct": attendance,
                                "Study_Hours_Per_Day": study,
                                "Previous_CGPA": previous_cgpa,
                                "Sleep_Hours": sleep,
                                "Social_Hours_Week": social,
                                "Final_CGPA": final_cgpa
                            }
                        ]
                    )

                    # Automatically calculate Grade
                    new_student["Grade"] = new_student[
                        "Final_CGPA"
                    ].apply(grade_from_cgpa)

                    # Automatically calculate Risk
                    new_student["Risk_Level"] = new_student.apply(
                        risk_from_row,
                        axis=1
                    )

                    # Add to existing dataset
                    updated_df = pd.concat(
                        [
                            df,
                            new_student
                        ],
                        ignore_index=True
                    )

                    # Save
                    save_students(
                        updated_df,
                        data_dir
                    )

                    # Remove old models
                    invalidate_models(
                        model_dir
                    )

                    st.success(
                        f"Student {sid} added successfully."
                    )

                    st.rerun()

    # =========================================================
    # UPDATE
    # =========================================================

    with tab3:

        st.subheader("Update Existing Student")

        if len(df) == 0:

            st.info(
                "No student records available."
            )

        else:

            selected_student = st.selectbox(
                "Select Student ID",
                df["Student_ID"]
                .astype(str)
                .tolist(),
                key="update_student_select"
            )

            selected_row = df[
                df["Student_ID"].astype(str)
                == selected_student
            ].iloc[0]

            st.markdown(
                f"""
                <div class="card">
                    <strong>Editing Student:</strong>
                    {selected_student}
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("update_student_form"):

                st.markdown("### Student Information")

                c1, c2, c3 = st.columns(3)

                with c1:

                    new_gender = st.selectbox(
                        "Gender",
                        sorted(
                            df["Gender"]
                            .dropna()
                            .astype(str)
                            .unique()
                            .tolist()
                        ),
                        index=sorted(
                            df["Gender"]
                            .dropna()
                            .astype(str)
                            .unique()
                            .tolist()
                        ).index(
                            str(selected_row["Gender"])
                        )
                    )

                with c2:

                    new_age = st.number_input(
                        "Age",
                        min_value=15,
                        max_value=60,
                        value=int(selected_row["Age"])
                    )

                with c3:

                    majors = sorted(
                        df["Major"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )

                    new_major = st.selectbox(
                        "Major",
                        majors,
                        index=majors.index(
                            str(selected_row["Major"])
                        )
                    )

                st.markdown(
                    "### Academic & Lifestyle Information"
                )

                c1, c2 = st.columns(2)

                with c1:

                    new_attendance = st.slider(
                        "Attendance (%)",
                        0.0,
                        100.0,
                        float(selected_row["Attendance_Pct"]),
                        0.5,
                        key="update_attendance"
                    )

                    new_study = st.slider(
                        "Study Hours / Day",
                        0.0,
                        16.0,
                        float(selected_row["Study_Hours_Per_Day"]),
                        0.5,
                        key="update_study"
                    )

                    new_previous_cgpa = st.slider(
                        "Previous CGPA",
                        0.0,
                        4.0,
                        float(selected_row["Previous_CGPA"]),
                        0.01,
                        key="update_previous_cgpa"
                    )

                with c2:

                    new_sleep = st.slider(
                        "Sleep Hours",
                        0.0,
                        14.0,
                        float(selected_row["Sleep_Hours"]),
                        0.5,
                        key="update_sleep"
                    )

                    new_social = st.slider(
                        "Social Hours / Week",
                        0.0,
                        60.0,
                        float(selected_row["Social_Hours_Week"]),
                        0.5,
                        key="update_social"
                    )

                    new_final_cgpa = st.slider(
                        "Final CGPA",
                        0.0,
                        4.0,
                        float(selected_row["Final_CGPA"]),
                        0.01,
                        key="update_final_cgpa"
                    )

                update_button = st.form_submit_button(
                    "💾 Save Student Changes",
                    use_container_width=True
                )

                if update_button:

                    # Locate student
                    mask = (
                        df["Student_ID"]
                        .astype(str)
                        == selected_student
                    )

                    # Update information
                    df.loc[
                        mask,
                        "Gender"
                    ] = new_gender

                    df.loc[
                        mask,
                        "Age"
                    ] = new_age

                    df.loc[
                        mask,
                        "Major"
                    ] = new_major

                    df.loc[
                        mask,
                        "Attendance_Pct"
                    ] = new_attendance

                    df.loc[
                        mask,
                        "Study_Hours_Per_Day"
                    ] = new_study

                    df.loc[
                        mask,
                        "Previous_CGPA"
                    ] = new_previous_cgpa

                    df.loc[
                        mask,
                        "Sleep_Hours"
                    ] = new_sleep

                    df.loc[
                        mask,
                        "Social_Hours_Week"
                    ] = new_social

                    df.loc[
                        mask,
                        "Final_CGPA"
                    ] = new_final_cgpa

                    # Recalculate Grade and Risk
                    updated_row = df.loc[
                        mask
                    ].iloc[0]

                    df.loc[
                        mask,
                        "Grade"
                    ] = grade_from_cgpa(
                        new_final_cgpa
                    )

                    df.loc[
                        mask,
                        "Risk_Level"
                    ] = risk_from_row(
                        updated_row
                    )

                    # Save changes
                    save_students(
                        df,
                        data_dir
                    )

                    # Remove old ML models
                    invalidate_models(
                        model_dir
                    )

                    st.success(
                        f"Student {selected_student} updated successfully."
                    )

                    st.rerun()

    # =========================================================
    # DELETE
    # =========================================================

    with tab4:

        st.subheader("Delete Student")

        st.warning(
            "⚠️ Deleting a student is permanent. "
            "The student will be removed from the college dataset."
        )

        if len(df) == 0:

            st.info(
                "No students available to delete."
            )

        else:

            delete_student = st.selectbox(
                "Select Student to Delete",
                df["Student_ID"]
                .astype(str)
                .tolist(),
                key="delete_student_select"
            )

            student_record = df[
                df["Student_ID"].astype(str)
                == delete_student
            ].iloc[0]

            st.markdown(
                f"""
                <div class="card">
                    <h3>Student Information</h3>

                    <p>
                    <strong>Student ID:</strong>
                    {student_record["Student_ID"]}
                    </p>

                    <p>
                    <strong>Major:</strong>
                    {student_record["Major"]}
                    </p>

                    <p>
                    <strong>Final CGPA:</strong>
                    {student_record["Final_CGPA"]}
                    </p>

                    <p>
                    <strong>Risk Level:</strong>
                    {student_record["Risk_Level"]}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("")

            confirm_delete = st.checkbox(
                "I understand that this action cannot be undone.",
                key="confirm_delete"
            )

            if st.button(
                "🗑️ Delete Student",
                type="primary",
                use_container_width=True
            ):

                if not confirm_delete:

                    st.error(
                        "Please confirm the deletion first."
                    )

                else:

                    # Remove student
                    updated_df = df[
                        df["Student_ID"].astype(str)
                        != delete_student
                    ].copy()

                    # Save updated dataset
                    save_students(
                        updated_df,
                        data_dir
                    )

                    # Remove old ML models
                    invalidate_models(
                        model_dir
                    )

                    st.success(
                        f"Student {delete_student} "
                        "was deleted successfully."
                    )

                    st.rerun()
