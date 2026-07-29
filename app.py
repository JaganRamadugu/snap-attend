import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen


def init_session():
    # Page / routing states
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None
        
    # Teacher authentication & view states
    if 'teacher_logged_in' not in st.session_state:
        st.session_state['teacher_logged_in'] = False
    if 'teacher_user' not in st.session_state:
        st.session_state['teacher_user'] = None
    if 'teacher_view' not in st.session_state:
        st.session_state['teacher_view'] = 'dashboard'
    if 'teacher_mode' not in st.session_state:
        st.session_state['teacher_mode'] = 'register'
        
    # Teacher scanner states
    if 'scanner_photos' not in st.session_state:
        st.session_state['scanner_photos'] = []
    if 'detection_results' not in st.session_state:
        st.session_state['detection_results'] = None
    if 'saved_disk_paths' not in st.session_state:
        st.session_state['saved_disk_paths'] = []


def main():
    init_session()
    
    # Read query parameters for auto-routing/context
    query_params = st.query_params
    if 'login_type' in query_params:
        st.session_state['login_type'] = query_params['login_type']
    
    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()


main()

