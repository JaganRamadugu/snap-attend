from src.ui.base_layout import style_base_layout,style_background_home
import streamlit as st
from src.components.header import header_home
def home_screen():


    header_home()
    style_background_home()
    style_base_layout()


    # 3-column layout to center the teacher card
    _, col_teacher, _ = st.columns([1.5, 3.5, 1.5])

    with col_teacher:
        # Invisible card marker to trigger CSS target
        st.markdown('<div class="card-marker"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-header">
            <span class="card-sub-header">I'm</span>
            <span class="card-main-header">Teacher</span>
        </div>
        """, unsafe_allow_html=True)
        st.image("src/images/teacher.png", width="stretch")
        if st.button("Teacher Portal ↗"):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    # Footer Branding
    st.markdown("""
    <div class="footer-branding">
        Created with <span class="heart">❤️</span> by <span style="color: #F18805; font-weight: 700;">Jagan</span> <span style="color: #F0A202; font-weight: 700;">Ramadugu</span>
    </div>
    """, unsafe_allow_html=True)