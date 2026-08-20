"""
ATTENDX AI - Global Header Component

Contains header rendering functions used across different views of the application.
Encodes the local logo.png image as base64 to inject it safely into raw HTML templates,
maintaining a clean and premium visual design.
"""

import streamlit as st
import base64

def header_home():
    """
    Renders a centered logo header on the home landing screen.
    Reads and base64-encodes src/images/logo.png.
    """
    try:
        with open("src/images/logo.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        img_src = f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        img_src = ""

    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px">
        <img src="{img_src}" style="height: 100px;"/>
    </div>
    """, unsafe_allow_html=True)


def header_portal():
    """
    Renders the header layout inside sub-portal screens (Teacher and Student).
    Displays the logo on the left and a quick navigation "Go back to Home" button on the right.
    """
    try:
        with open("src/images/logo.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        img_src = f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        img_src = ""

    col_logo, col_back = st.columns([3, 1.5])
    with col_logo:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-top: 10px;">
            <img src="{img_src}" style="height: 60px;"/>
        </div>
        """, unsafe_allow_html=True)
    with col_back:
        # Extra spacing wrapper to align the button vertically with the logo
        st.markdown('<div style="display:flex; justify-content:flex-end; margin-top: 10px;">', unsafe_allow_html=True)
        if st.button("Go back to Home ⌘ + Backspace", key="back_to_home", type="secondary"):
            st.session_state['login_type'] = None
            st.query_params.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    