"""
ATTENDX AI - Student Portal Screen

Renders the student biometric enrollment and registration workspace. Enables students
to input their ID, capture a high-definition selfie, extract a 128-dimensional face
embedding, and register their profile. It also supports automated course enrollment
via QR code-supplied subject contexts.
"""

import streamlit as st
from src.ui.base_layout import style_base_layout, style_background_dashboard
from src.components.header import header_portal
from src.database.db import (
    check_student_exists, 
    create_student, 
    get_student_by_id, 
    enroll_student_in_subject, 
    is_student_enrolled, 
    get_subject_by_id
)
from src.pipelines.face_pipeline import get_face_embeddings, train_classifier
from PIL import Image
import numpy as np

def student_screen():
    """
    Renders the student biometric setup view. Handles registration forms,
    interactive camera input for face photo capture, checks existing registration records,
    and runs enrollment hooks when a valid subject ID context is passed in URL query parameters.
    """
    style_background_dashboard()
    style_base_layout()
    
    header_portal()
    
    # Read query parameters for subject_id if present (enables QR-code auto enrollment)
    query_params = st.query_params
    subject_id_str = query_params.get("subject_id", None)
    subject = None
    if subject_id_str:
        try:
            subject = get_subject_by_id(int(subject_id_str))
        except Exception:
            pass

    _, col_main, _ = st.columns([1, 4, 1])
    
    with col_main:
        # Title Branding Card
        st.markdown("""
        <div style="background-color: #FFFFFF; border-radius: 24px; padding: 35px; border: 2px solid #7B9E89; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); margin-top: 10px; margin-bottom: 30px;">
            <h1 style="color: #0E1428; margin-top: 0; text-align: center; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; margin-bottom: 5px;">Student Biometric Setup</h1>
            <p style="color: #7B9E89; font-size: 1rem; text-align: center; margin-bottom: 25px;">Register your face profile to enable automatic attendance tracking.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display class context information if redirected from a teacher's classroom QR code
        if subject:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #EFEFFA 0%, #E2F1E8 100%); border-radius: 16px; padding: 20px; border: 1.5px solid #7B9E89; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.8rem; line-height: 1;">📚</span>
                    <div>
                        <h4 style="margin: 0; color: #0E1428; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 1.1rem;">Enrolling in Class</h4>
                        <p style="margin: 3px 0 0 0; color: #4A5568; font-size: 0.95rem; font-weight: 600;">
                            {subject['subject_code']} - {subject['name']} (Section {subject['section']})
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Form Field: Student identification number
        student_id_str = st.text_input("Student ID (Integer Number)", placeholder="e.g. 10024", key="student_id_input")
        
        # Check if student is already in the database
        student_id = None
        existing_student = None
        if student_id_str.strip():
            try:
                student_id = int(student_id_str.strip())
                if student_id > 0:
                    existing_student = get_student_by_id(student_id)
            except ValueError:
                pass

        if existing_student:
            # Welcome the registered student and guide them to enroll or check enrollment status
            st.markdown(f"""
            <div style="background-color: #E2F1E8; border: 1.5px solid #7B9E89; padding: 15px; border-radius: 12px; margin-bottom: 20px;">
                <p style="color: #0E1428; margin: 0; font-weight: 600;">👋 Welcome back, <b>{existing_student['name']}</b>!</p>
                <p style="color: #4A5568; margin: 5px 0 0 0; font-size: 0.9rem;">Your biometric face profile is already registered.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if subject:
                # Resolve subject enrollment context
                already_enrolled = is_student_enrolled(student_id, subject['subject_id'])
                if already_enrolled:
                    st.info(f"You are already enrolled in **{subject['subject_code']} - {subject['name']}**!")
                else:
                    if st.button(f"🔗 Confirm Enrollment in {subject['subject_code']}", use_container_width=True, type="primary"):
                        with st.spinner("Enrolling..."):
                            try:
                                enroll_student_in_subject(student_id, subject['subject_id'])
                                st.success(f"🎉 Successfully enrolled in **{subject['subject_code']} - {subject['name']}**!")
                                st.balloons()
                            except Exception as e:
                                st.error(f"Failed to enroll: {e}")
            else:
                st.info("Your face profile is registered. To enroll in a class, please scan the class QR code.")
                
        else:
            # Render registration form fields for new student profile registration
            name = st.text_input("Full Name", placeholder="e.g. John Doe", key="student_name")
            
            st.write("")
            st.markdown("<h4 style='color: #0E1428; margin-bottom: 5px; font-weight: 600;'>📸 Biometric Photo Capture</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color: #4A5568; font-size: 0.9rem; margin-top: 0; margin-bottom: 15px;'>Position your face in the center of the frame and click 'Take Photo'.</p>", unsafe_allow_html=True)
            
            # Interactive camera capture utility
            img_file = st.camera_input("Capture Photo", label_visibility="collapsed")
            
            st.write("")
            
            # Submission logic
            if st.button("🚀 Register & Save Profile", use_container_width=True, type="primary"):
                # Input validation checks
                if not name.strip():
                    st.error("Please enter your name.")
                elif not student_id_str.strip():
                    st.error("Please enter your Student ID.")
                elif not img_file:
                    st.error("Please capture your photo before registering.")
                else:
                    try:
                        student_id = int(student_id_str.strip())
                        if student_id <= 0:
                            st.error("Student ID must be a positive integer.")
                            return
                    except ValueError:
                        st.error("Student ID must be a valid integer number (e.g. 12345).")
                        return
                    
                    with st.spinner("Processing biometric data & registering profile... Please wait."):
                        try:
                            # Convert uploaded snapshot to PIL Image and cast to numpy matrix (RGB)
                            image = Image.open(img_file)
                            image_np = np.array(image.convert("RGB"))
                            
                            # Extract 128-dimensional face embedding using Dlib models
                            embeddings = get_face_embeddings(image_np)
                            
                            if len(embeddings) == 0:
                                st.error("❌ No face detected in the photo. Please align your face clearly in the camera and try again.")
                            elif len(embeddings) > 1:
                                st.error("❌ Multiple faces detected in the photo. Please ensure only you are visible in the camera frame.")
                            else:
                                embedding_list = embeddings[0].tolist()
                                
                                # 1. Create the student database profile (stores the embedding)
                                create_student(student_id, name.strip(), embedding_list)
                                
                                # 2. Force invalidate cache and reload classification models
                                train_classifier()
                                
                                # 3. Auto-enroll in subject if a classroom query parameter context is present
                                enrollment_msg = ""
                                if subject:
                                    enroll_student_in_subject(student_id, subject['subject_id'])
                                    enrollment_msg = f" and enrolled in **{subject['subject_code']} - {subject['name']}**"
                                
                                st.success(f"🎉 Profile successfully created for **{name.strip()}** (ID: {student_id}){enrollment_msg}!")
                                st.balloons()
                        except Exception as e:
                            st.error(f"Failed to register student profile: {e}")



         