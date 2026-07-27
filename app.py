import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen


def main():
    # Read query parameters for auto-routing/context
    query_params = st.query_params
    if 'login_type' in query_params:
        st.session_state['login_type'] = query_params['login_type']

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None
    
    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()


main()

