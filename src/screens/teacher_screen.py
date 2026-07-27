import streamlit as st
import io
import os
import time
import segno
import pandas as pd
from PIL import Image
import numpy as np
from src.ui.base_layout import style_base_layout, style_background_dashboard
from src.components.header import header_portal
from src.database.db import (
    check_teacher_exists, 
    create_teacher, 
    teacher_login, 
    create_subject, 
    get_subjects_by_teacher, 
    log_attendance, 
    get_attendance_reports, 
    get_all_students
)
from src.pipelines.face_pipeline import predict_attendance

def teacher_screen():
    style_background_dashboard()
    style_base_layout()
    
    if 'teacher_mode' not in st.session_state:
        st.session_state['teacher_mode'] = 'register'
        
    if 'teacher_logged_in' not in st.session_state:
        st.session_state['teacher_logged_in'] = False

    if 'teacher_view' not in st.session_state:
        st.session_state['teacher_view'] = 'dashboard'

    # Render top header with logo and Go back button
    header_portal()

    if st.session_state['teacher_logged_in']:
        match st.session_state['teacher_view']:
            case 'dashboard':
                render_teacher_dashboard()
            case 'scanner':
                render_scanner_view()
            case 'classes':
                render_classes_view()
            case 'reports':
                render_reports_view()
            case 'qr':
                render_qr_view()
    else:
        render_auth_flow()

def render_teacher_dashboard():
    teacher = st.session_state.get('teacher_user', {})
    teacher_name = teacher.get('name', 'Teacher')
    
    st.markdown(f'<h1 style="text-align: center; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 2.5rem; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 5px;">Welcome back, {teacher_name}!</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7B9E89; font-family: \'Inter\', sans-serif; font-size: 1.1rem; margin-bottom: 30px;">Teacher Dashboard | Snap Attend Portal</p>', unsafe_allow_html=True)
    
    # Grid of controls / actions
    col_act1, col_act2 = st.columns(2)
    
    with col_act1:
        st.markdown("""
        <div style="background-color: #EFEFFA; border-radius: 20px; padding: 25px; border: 2px solid #7B9E89; margin-bottom: 20px;">
            <h3 style="color: #0E1428; margin-top: 0;">📸 AI Attendance</h3>
            <p style="color: #4a5568; font-size: 0.95rem;">Start automatic face recognition attendance scanning using a webcam feed.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Scanner ↗", key="btn_scanner", type="primary", width="stretch"):
            st.session_state['teacher_view'] = 'scanner'
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #EFEFFA; border-radius: 20px; padding: 25px; border: 2px solid #7B9E89; margin-bottom: 20px;">
            <h3 style="color: #0E1428; margin-top: 0;">➕ Add Class</h3>
            <p style="color: #4a5568; font-size: 0.95rem;">Configure new student cohorts, semesters, and subjects to manage attendance tracker.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Configure Classes", key="btn_classes", type="secondary", width="stretch"):
            st.session_state['teacher_view'] = 'classes'
            st.rerun()
            
    with col_act2:
        st.markdown("""
        <div style="background-color: #EFEFFA; border-radius: 20px; padding: 25px; border: 2px solid #7B9E89; margin-bottom: 20px;">
            <h3 style="color: #0E1428; margin-top: 0;">📱 QR Attendance</h3>
            <p style="color: #4a5568; font-size: 0.95rem;">Generate dynamic temporary QR code for students to scan and register attendance.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Generate QR Code", key="btn_qr", type="primary", width="stretch"):
            st.session_state['teacher_view'] = 'qr'
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #EFEFFA; border-radius: 20px; padding: 25px; border: 2px solid #7B9E89; margin-bottom: 20px;">
            <h3 style="color: #0E1428; margin-top: 0;">📊 Reports & Logs</h3>
            <p style="color: #4a5568; font-size: 0.95rem;">Export attendance spreadsheets, review logs, and view percentage insights.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Reports", key="btn_reports", type="secondary", width="stretch"):
            st.session_state['teacher_view'] = 'reports'
            st.rerun()
            
    st.write("")
    st.write("")
    if st.button("🚪 Logout from Portal", key="btn_logout", type="secondary", width="stretch"):
        st.session_state['teacher_logged_in'] = False
        st.session_state['teacher_user'] = None
        st.session_state['teacher_view'] = 'dashboard'
        st.rerun()

    # Footer Branding
    st.markdown("""
    <div class="footer-branding" style="margin-top: 60px;">
        Created with <span class="heart">❤️</span> by <span style="color: #F18805; font-weight: 700;">Jagan</span> <span style="color: #F0A202; font-weight: 700;">Ramadugu</span>
    </div>
    """, unsafe_allow_html=True)

def render_classes_view():
    teacher = st.session_state.get('teacher_user', {})
    teacher_id = teacher.get('teacher_id')
    
    st.markdown('<h2 style="text-align: center; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 5px;">Class Configuration</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7B9E89; margin-bottom: 25px;">Manage your student cohorts and subjects</p>', unsafe_allow_html=True)
    
    if st.button("⬅ Back to Dashboard", key="back_from_classes", type="secondary"):
        st.session_state['teacher_view'] = 'dashboard'
        st.rerun()
        
    st.write("")
    
    col_add, col_list = st.columns([1.2, 1.8])
    
    with col_add:
        st.markdown("<h4 style='color: #0E1428; font-weight: 700; margin-top: 0;'>➕ Add New Class/Subject</h4>", unsafe_allow_html=True)
        sub_code = st.text_input("Subject Code", placeholder="e.g. CS101", key="class_sub_code")
        sub_name = st.text_input("Subject Name", placeholder="e.g. Data Structures", key="class_sub_name")
        sub_section = st.text_input("Section", placeholder="e.g. A", key="class_sub_section")
        
        if st.button("Create Class", type="primary", width="stretch"):
            if not sub_code.strip() or not sub_name.strip() or not sub_section.strip():
                st.error("Please fill in all fields.")
            else:
                try:
                    create_subject(sub_code.strip(), sub_name.strip(), sub_section.strip(), teacher_id)
                    st.success(f"Class '{sub_name}' created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create class: {e}")
                    
    with col_list:
        st.markdown("<h4 style='color: #0E1428; font-weight: 700; margin-top: 0;'>📚 Configured Classes</h4>", unsafe_allow_html=True)
        subjects = get_subjects_by_teacher(teacher_id)
        
        if not subjects:
            st.info("You haven't configured any classes yet. Use the form on the left to add one.")
        else:
            df = pd.DataFrame(subjects)
            df = df[['subject_id', 'subject_code', 'name', 'section']]
            df.columns = ['ID', 'Code', 'Subject Name', 'Section']
            st.dataframe(df, width="stretch", hide_index=True)

def render_qr_view():
    teacher = st.session_state.get('teacher_user', {})
    teacher_id = teacher.get('teacher_id')
    
    st.markdown('<h2 style="text-align: center; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 5px;">QR Attendance Generator</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7B9E89; margin-bottom: 25px;">Generate a session QR code for student check-in</p>', unsafe_allow_html=True)
    
    if st.button("⬅ Back to Dashboard", key="back_from_qr", type="secondary"):
        st.session_state['teacher_view'] = 'dashboard'
        st.rerun()
        
    st.write("")
    
    subjects = get_subjects_by_teacher(teacher_id)
    if not subjects:
        st.warning("Please configure at least one class before generating a QR code.")
        return
        
    subject_options = {f"{s['subject_code']} - {s['name']} (Sec {s['section']})": s['subject_id'] for s in subjects}
    selected_sub_label = st.selectbox("Select Class", list(subject_options.keys()))
    subject_id = subject_options[selected_sub_label]
    
    import time
    import socket
    
    # 1. Resolve host IP for local network connections
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"

    # 2. Get host name from browser context headers
    host = "localhost:8501"
    try:
        # Check if st.context is available in this Streamlit version
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            browser_host = st.context.headers.get("host") or st.context.headers.get("Host")
            if browser_host:
                host = browser_host
    except Exception:
        pass

    # 3. If accessed locally, replace localhost/127.0.0.1 with local IP for mobile access
    if "localhost" in host or "127.0.0.1" in host:
        local_ip = get_local_ip()
        host = host.replace("localhost", local_ip).replace("127.0.0.1", local_ip)

    # 4. Generate url (use https if deployed globally, fallback to http)
    protocol = "https" if not any(ip_val in host for ip_val in ["192.168.", "10.", "172.", "localhost", "127.0.0.1"]) else "http"
    
    token = f"class_{subject_id}_time_{int(time.time())}"
    scan_url = f"{protocol}://{host}/?login_type=student&subject_id={subject_id}&token={token}"
    
    col_qr, col_info = st.columns([1, 1])
    
    with col_qr:
        qr = segno.make_qr(scan_url)
        buffer = io.BytesIO()
        qr.save(buffer, kind="png", scale=10)
        st.image(buffer.getvalue(), caption="Scan to Register Attendance", width="stretch")
        
    with col_info:
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border-radius: 16px; padding: 20px; border: 1px solid #7B9E89; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <h4 style="color: #0E1428; margin-top: 0;">📱 Active QR Code Details</h4>
            <p><b>Class:</b> {selected_sub_label}</p>
            <p><b>Secure Token:</b> <code style="font-size: 0.85rem;">{token}</code></p>
            <p><b>Link:</b> <a href="{scan_url}" target="_blank" style="word-break: break-all; color: #7B9E89; text-decoration: none; font-weight: 600;">{scan_url}</a></p>
            <p style="color: #4a5568; font-size: 0.9rem; line-height: 1.4; margin-top: 10px;">Students can scan this QR code using their mobile devices to navigate directly to the biometric portal with this class context pre-selected.</p>
        </div>
        """, unsafe_allow_html=True)

def cleanup_old_uploads():
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        return
    now = time.time()
    cutoff = now - 24 * 3600  # 24 hours
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        if os.path.isfile(file_path):
            try:
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff:
                    os.remove(file_path)
            except Exception:
                pass

def save_uploaded_image(img_file):
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir, exist_ok=True)
    try:
        # Generate clean timestamped filename
        suffix = img_file.name if hasattr(img_file, "name") and img_file.name else "camera.jpg"
        # Sanitize filename
        safe_suffix = "".join(c for c in suffix if c.isalnum() or c in (".", "_", "-"))
        filename = f"att_{int(time.time())}_{safe_suffix}"
        file_path = os.path.join(uploads_dir, filename)
        
        # Save file to disk
        img_file.seek(0)
        with open(file_path, "wb") as f:
            f.write(img_file.read())
        img_file.seek(0)  # reset for subsequent PIL read
    except Exception:
        pass

def render_scanner_view():
    cleanup_old_uploads()
    teacher = st.session_state.get('teacher_user', {})
    teacher_id = teacher.get('teacher_id')
    
    st.markdown('<h2 style="text-align: center; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 5px;">AI Attendance Scanner</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7B9E89; margin-bottom: 25px;">Take or upload a class photo to automatically register attendance</p>', unsafe_allow_html=True)
    
    if st.button("⬅ Back to Dashboard", key="back_from_scanner", type="secondary"):
        st.session_state['teacher_view'] = 'dashboard'
        st.rerun()
        
    st.write("")
    
    subjects = get_subjects_by_teacher(teacher_id)
    if not subjects:
        st.warning("Please configure at least one class/subject before running the scanner.")
        return
        
    subject_options = {f"{s['subject_code']} - {s['name']} (Sec {s['section']})": s['subject_id'] for s in subjects}
    selected_sub_label = st.selectbox("Select Class/Subject", list(subject_options.keys()))
    subject_id = subject_options[selected_sub_label]
    
    st.markdown("<h4 style='color: #0E1428; font-weight: 700;'>📸 Class Group Photo</h4>", unsafe_allow_html=True)
    
    tab_camera, tab_upload = st.tabs(["📷 Use Camera Input", "📤 Upload Photo File"])
    img_file = None
    
    with tab_camera:
        cam_file = st.camera_input("Capture Group Image", label_visibility="collapsed")
        if cam_file:
            img_file = cam_file
            
    with tab_upload:
        uploaded_file = st.file_uploader("Upload a group photo...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_file:
            if uploaded_file.size > 50 * 1024 * 1024:
                st.error("❌ File size exceeds the 50MB limit.")
            else:
                img_file = uploaded_file
            
    if img_file:
        save_uploaded_image(img_file)
        image = Image.open(img_file)
        image_np = np.array(image.convert("RGB"))
        
        with st.spinner("Analyzing class photo using AI Face Pipeline..."):
            try:
                # Run prediction
                detected, all_registered_ids, num_faces = predict_attendance(image_np)
                
                # Fetch all registered students
                students = get_all_students()
                student_map = {s['student_id']: s for s in students}
                
                st.write("")
                st.markdown(f"### 📊 Scan Results (Detected {num_faces} faces)")
                
                if not students:
                    st.info("No registered students found in the database. Go to Student Portal to register student profiles first.")
                    return
                
                # We want to display the attendance list
                attendance_list = []
                for s_id, student in student_map.items():
                    is_present = detected.get(s_id, False)
                    attendance_list.append({
                        'student_id': s_id,
                        'name': student['name'],
                        'status': '✅ Present' if is_present else '❌ Absent',
                        'is_present': is_present
                    })
                
                df_att = pd.DataFrame(attendance_list)
                
                col_table, col_summary = st.columns([2, 1])
                
                with col_table:
                    st.dataframe(
                        df_att[['student_id', 'name', 'status']], 
                        width="stretch", 
                        hide_index=True
                    )
                    
                with col_summary:
                    present_count = sum(1 for a in attendance_list if a['is_present'])
                    absent_count = len(attendance_list) - present_count
                    rate = (present_count / len(attendance_list)) * 100 if attendance_list else 0
                    
                    st.markdown(f"""
                    <div style="background-color: #FFFFFF; border-radius: 16px; padding: 20px; border: 1px solid #7B9E89; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <h4 style="color: #0E1428; margin-top: 0;">Summary</h4>
                        <p style="font-size: 1.1rem; margin-bottom: 5px;"><b>Total Students:</b> {len(attendance_list)}</p>
                        <p style="font-size: 1.1rem; margin-bottom: 5px; color: green;"><b>Present:</b> {present_count}</p>
                        <p style="font-size: 1.1rem; margin-bottom: 5px; color: red;"><b>Absent:</b> {absent_count}</p>
                        <p style="font-size: 1.2rem; font-weight: 700; margin-top: 15px; color: #F18805;">Attendance: {rate:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("")
                if st.button("💾 Save & Log Attendance", type="primary", width="stretch"):
                    with st.spinner("Saving logs to database..."):
                        for item in attendance_list:
                            log_attendance(item['student_id'], subject_id, item['is_present'])
                        st.success(f"Attendance logged successfully for class '{selected_sub_label}'!")
                        st.balloons()
            except Exception as e:
                st.error(f"Error executing AI Attendance pipeline: {e}")

def render_reports_view():
    teacher = st.session_state.get('teacher_user', {})
    teacher_id = teacher.get('teacher_id')
    
    st.markdown('<h2 style="text-align: center; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 5px;">Attendance Reports & Logs</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7B9E89; margin-bottom: 25px;">Export, view history, and filter student attendance</p>', unsafe_allow_html=True)
    
    if st.button("⬅ Back to Dashboard", key="back_from_reports", type="secondary"):
        st.session_state['teacher_view'] = 'dashboard'
        st.rerun()
        
    st.write("")
    
    subjects = get_subjects_by_teacher(teacher_id)
    if not subjects:
        st.warning("Please configure a class first to view logs.")
        return
        
    subject_options = {f"{s['subject_code']} - {s['name']} (Sec {s['section']})": s['subject_id'] for s in subjects}
    selected_sub_label = st.selectbox("Select Class", list(subject_options.keys()))
    subject_id = subject_options[selected_sub_label]
    
    with st.spinner("Fetching logs..."):
        logs = get_attendance_reports(subject_id)
        students = get_all_students()
        student_map = {s['student_id']: s['name'] for s in students}
        
    if not logs:
        st.info("No attendance logs found for this class.")
        return
        
    log_data = []
    for log in logs:
        s_id = log['student_id']
        s_name = student_map.get(s_id, f"Unknown Student (ID: {s_id})")
        
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(log['timestamp'].replace("Z", "+00:00"))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            formatted_time = log['timestamp']
            
        log_data.append({
            'Timestamp': formatted_time,
            'Student ID': s_id,
            'Student Name': s_name,
            'Status': '✅ Present' if log['is_present'] else '❌ Absent'
        })
        
    df_logs = pd.DataFrame(log_data)
    
    col_total, col_present_rate = st.columns(2)
    total_records = len(df_logs)
    present_records = sum(1 for l in log_data if 'Present' in l['Status'])
    overall_rate = (present_records / total_records) * 100 if total_records else 0
    
    with col_total:
        st.metric("Total Records logged", total_records)
    with col_present_rate:
        st.metric("Overall Attendance Rate", f"{overall_rate:.1f}%")
        
    st.write("")
    
    csv = df_logs.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Report as CSV",
        data=csv,
        file_name=f"attendance_report_{subject_id}.csv",
        mime="text/csv",
        width="stretch"
    )
    
    st.write("")
    st.dataframe(df_logs, width="stretch", hide_index=True)

def render_auth_flow():
    _, col_form, _ = st.columns([1, 3.5, 1])

    with col_form:
        if st.session_state['teacher_mode'] == 'register':
            st.markdown('<h1 style="text-align: center; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 2.3rem; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 25px;">Register your teacher profile</h1>', unsafe_allow_html=True)
            
            username = st.text_input("Enter username", placeholder="@abhishek", key="reg_username")
            name = st.text_input("Enter name", placeholder="Abhishek Sharma", key="reg_name")

            password = st.text_input("Enter password", type="password", placeholder="Enter your password", key="reg_password")
            confirm_password = st.text_input("Confirm password", type="password", placeholder="Confirm your password", key="reg_confirm_password")
            
            st.write("")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("👤+ Register Now ⌘ + Enter", key="btn_register", type="primary", width="stretch"):
                    if not username or not name or not password or not confirm_password:
                        st.error("Please fill in all fields.")
                    elif password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        if check_teacher_exists(username):
                            st.error("Username already exists. Please choose a different username.")
                        else:
                            try:
                                create_teacher(username, password, name)
                                st.success(f"Teacher profile registered successfully for {name}!")
                                st.session_state['teacher_mode'] = 'login'
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to register teacher: {e}")
                        
            with col_btn2:
                if st.button("👤 Login instead", key="btn_login_instead", type="secondary", width="stretch"):
                    st.session_state['teacher_mode'] = 'login'
                    st.rerun()
                    
        else:
            st.markdown('<h1 style="text-align: center; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 2.3rem; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 25px;">Login to your teacher profile</h1>', unsafe_allow_html=True)
            
            username = st.text_input("Enter username", placeholder="@abhishek", key="login_username")
            password = st.text_input("Enter password", type="password", placeholder="Enter your password", key="login_password")
            
            st.write("")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔑 Login Now ⌘ + Enter", key="btn_login", type="primary", width="stretch"):
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        teacher = teacher_login(username, password)
                        if teacher:
                            st.session_state['teacher_logged_in'] = True
                            st.session_state['teacher_user'] = teacher
                            st.session_state['teacher_view'] = 'dashboard'
                            st.success(f"Welcome back, {teacher.get('name', username)}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                        
            with col_btn2:
                if st.button("👤+ Register instead", key="btn_register_instead", type="secondary", width="stretch"):
                    st.session_state['teacher_mode'] = 'register'
                    st.rerun()

    # Footer Branding
    st.markdown("""
    <div class="footer-branding" style="margin-top: 60px;">
        Created with <span class="heart">❤️</span> by <span style="color: #F18805; font-weight: 700;">Jagan</span> <span style="color: #F0A202; font-weight: 700;">Ramadugu</span>
    </div>
    """, unsafe_allow_html=True)