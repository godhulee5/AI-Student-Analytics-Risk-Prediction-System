from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
from utils.data_manager import load_students, load_interventions, save_intervention


def render(data_dir, model_dir):
    df = load_students(data_dir)
    interventions = load_interventions(data_dir)
    st.markdown("""<div class='hero'><h1>Intervention Management</h1><p>Record mentor actions and follow-up status for students requiring support.</p></div>""", unsafe_allow_html=True)
    ids = sorted(df["Student_ID"].astype(str).unique())
    if not ids:
        st.warning("No students available.")
        return
    with st.form("intervention_form"):
        sid = st.selectbox("Student ID", ids)
        mentor = st.text_input("Mentor / Staff Name")
        action = st.selectbox("Intervention Type", ["Mentoring", "Academic Support", "Counselling", "Attendance Follow-up", "Parent/Guardian Contact", "Other"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        followup = st.date_input("Follow-up Date")
        notes = st.text_area("Notes / Action Taken", placeholder="Describe the support provided and next steps.")
        submitted = st.form_submit_button("Save Intervention", type="primary", use_container_width=True)
    if submitted:
        if not mentor.strip() or not notes.strip():
            st.error("Please enter the mentor/staff name and intervention notes.")
        else:
            save_intervention(data_dir, sid, mentor.strip(), action, status, str(followup), notes.strip())
            st.success("Intervention record saved.")
            st.rerun()
    st.subheader("Intervention History")
    if interventions.empty:
        st.info("No interventions have been recorded yet.")
        return
    filtered = interventions.copy()
    sid_filter = st.selectbox("Filter by student", ["All Students"] + ids, key="intervention_filter")
    if sid_filter != "All Students":
        filtered = filtered[filtered["Student_ID"].astype(str) == sid_filter]
    st.dataframe(filtered.sort_values("Created_At", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download Intervention History", filtered.to_csv(index=False).encode("utf-8"), "intervention_history.csv", "text/csv")
