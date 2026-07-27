import streamlit as st
import base64

def header_home():
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
        # Extra spacing wrapper to align button
        st.markdown('<div style="display:flex; justify-content:flex-end; margin-top: 10px;">', unsafe_allow_html=True)
        if st.button("Go back to Home ⌘ + Backspace", key="back_to_home", type="secondary"):
            st.session_state['login_type'] = None
            st.query_params.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    