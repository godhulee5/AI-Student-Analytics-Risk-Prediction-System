import streamlit as st
from pathlib import Path
from utils.auth import require_admin, logout
from utils.data_manager import initialize_data
from utils.ml_engine import ensure_models
st.set_page_config(
    page_title="AI Student Analytics | Admin Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
# Global initialization
initialize_data(DATA_DIR)
ensure_models(DATA_DIR, MODEL_DIR)
require_admin()
# CSS
css_path = BASE_DIR / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🎓</div>
            <div>
                <div class="brand-title">StudentIQ</div>
                <div class="brand-sub">College Admin Portal</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### NAVIGATION")
    page = st.radio(
        "Open module",
        [
            "Dashboard",
            "Student Management",
            "Academic Analytics",
            "AI Risk Prediction",
            "Grade Prediction",
            "Early Warning System",
            "Student Progress Tracking",
            "Intervention Management",
            "Model Evaluation",
            "Reports",
            "Admin Panel",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        '<div class="sidebar-note">🔒 Admin-only access<br>AI outputs are decision-support indicators.</div>',
        unsafe_allow_html=True,
    )
    if st.button("Logout", use_container_width=True):
        logout()
# Route modules
if page == "Dashboard":
    from modules.dashboard import render
elif page == "Student Management":
    from modules.student_management import render
elif page == "Academic Analytics":
    from modules.academic_analytics import render
elif page == "AI Risk Prediction":
    from modules.risk_prediction import render
elif page == "Grade Prediction":
    from modules.grade_prediction import render
elif page == "Early Warning System":
    from modules.early_warning import render
elif page == "Student Progress Tracking":
    from modules.progress_tracking import render
elif page == "Intervention Management":
    from modules.intervention_management import render
elif page == "Model Evaluation":
    from modules.model_evaluation import render
elif page == "Reports":
    from modules.reports import render
elif page == "Admin Panel":
    from modules.admin_panel import render
render(DATA_DIR, MODEL_DIR)