import streamlit as st

DEMO_USERNAME = "admin"
DEMO_PASSWORD = "admin123"

def require_admin():
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.markdown(
            """
            <div class="login-box">
                <div style="font-size:42px">🎓</div>
                <h1 style="margin-bottom:4px">StudentIQ Admin</h1>
                <p style="color:#64748b">Secure college administration portal</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Admin username")
            password = st.text_input("Admin password", type="password")
            submitted = st.form_submit_button("Sign in", use_container_width=True)
            if submitted:
                if username == DEMO_USERNAME and password == DEMO_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid admin credentials.")
        st.info("Demo login: admin / admin123")
        st.stop()

def logout():
    st.session_state.admin_authenticated = False
    st.rerun()
