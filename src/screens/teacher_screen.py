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
    get_students_by_subject,
    delete_attendance_logs,
    clear_attendance_logs_by_subject,
    delete_subject
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
        st.session_state['teacher_mode'] = 'login'
        st.session_state['scanner_photos'] = []
        st.session_state['detection_results'] = None
        st.session_state['saved_disk_paths'] = []
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

def save_photo_to_disk(photo_bytes, photo_name):
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir, exist_ok=True)
    try:
        # Sanitize filename
        safe_suffix = "".join(c for c in photo_name if c.isalnum() or c in (".", "_", "-"))
        filename = f"att_{int(time.time())}_{safe_suffix}"
        file_path = os.path.join(uploads_dir, filename)
        with open(file_path, "wb") as f:
            f.write(photo_bytes)
        return file_path
    except Exception:
        return None

def render_scanner_view():
    cleanup_old_uploads()
    teacher = st.session_state.get('teacher_user', {})
    teacher_id = teacher.get('teacher_id')
    
    st.markdown('<h2 style="text-align: center; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 5px;">AI Attendance Scanner</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7B9E89; margin-bottom: 25px;">Take or upload up to 3 class photos to automatically register attendance</p>', unsafe_allow_html=True)
    
    # Initialize session state for multi-photo list
    if 'scanner_photos' not in st.session_state:
        st.session_state['scanner_photos'] = []
    if 'detection_results' not in st.session_state:
        st.session_state['detection_results'] = None
    if 'saved_disk_paths' not in st.session_state:
        st.session_state['saved_disk_paths'] = []

    if st.button("⬅ Back to Dashboard", key="back_from_scanner", type="secondary"):
        st.session_state['scanner_photos'] = []
        st.session_state['detection_results'] = None
        st.session_state['saved_disk_paths'] = []
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
    
    # Render Photo Gallery
    st.markdown("<h4 style='color: #0E1428; font-weight: 700; margin-top: 20px;'>📷 Active Photos (Up to 3)</h4>", unsafe_allow_html=True)
    
    if len(st.session_state['scanner_photos']) == 0:
        st.info("No photos added yet. Add photos below using your webcam or file upload.")
    else:
        # Display columns of added photos
        cols = st.columns(3)
        for i, photo in enumerate(st.session_state['scanner_photos']):
            with cols[i]:
                try:
                    img = Image.open(io.BytesIO(photo['data']))
                    st.image(img, caption=photo['name'], use_container_width=True)
                except Exception:
                    st.error("Failed to render preview.")
                
                if st.button(f"🗑️ Remove Photo {i+1}", key=f"btn_remove_{i}", type="secondary", width="stretch"):
                    st.session_state['scanner_photos'].pop(i)
                    st.session_state['detection_results'] = None
                    st.rerun()

    # Show adding options if less than 3
    if len(st.session_state['scanner_photos']) < 3:
        st.markdown("<h4 style='color: #0E1428; font-weight: 700; margin-top: 20px;'>➕ Add Photo</h4>", unsafe_allow_html=True)
        tab_camera, tab_upload = st.tabs(["📷 Use Camera Input", "📤 Upload Photo File"])
        
        with tab_camera:
            cam_file = st.camera_input("Capture Group Image", key=f"cam_input_{len(st.session_state['scanner_photos'])}", label_visibility="collapsed")
            if cam_file:
                if st.button("➕ Add Captured Photo", key="btn_add_cam", type="primary", width="stretch"):
                    photo_bytes = cam_file.getvalue()
                    name = f"camera_capture_{len(st.session_state['scanner_photos']) + 1}.jpg"
                    st.session_state['scanner_photos'].append({'name': name, 'data': photo_bytes})
                    st.session_state['detection_results'] = None
                    st.rerun()
                    
        with tab_upload:
            uploaded_files = st.file_uploader("Upload class photos...", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f"upload_input_{len(st.session_state['scanner_photos'])}", label_visibility="collapsed")
            if uploaded_files:
                if st.button("➕ Add Uploaded Photos", key="btn_add_upload", type="primary", width="stretch"):
                    added = False
                    for uf in uploaded_files:
                        if len(st.session_state['scanner_photos']) >= 3:
                            st.warning("Maximum of 3 photos reached. Skipping remaining files.")
                            break
                        if uf.size > 50 * 1024 * 1024:
                            st.error(f"❌ {uf.name} exceeds the 50MB limit.")
                            continue
                        
                        if not any(p['name'] == uf.name for p in st.session_state['scanner_photos']):
                            st.session_state['scanner_photos'].append({'name': uf.name, 'data': uf.getvalue()})
                            added = True
                    if added:
                        st.session_state['detection_results'] = None
                        st.rerun()

    # Trigger detection
    if len(st.session_state['scanner_photos']) > 0:
        st.write("")
        if st.button("🔍 Run AI Attendance Detection", key="btn_run_detection", type="primary", width="stretch"):
            with st.spinner("Analyzing class photos using AI Face Pipeline..."):
                try:
                    detected_union = {}
                    total_faces = 0
                    saved_paths = []
                    
                    for photo in st.session_state['scanner_photos']:
                        path = save_photo_to_disk(photo['data'], photo['name'])
                        if path:
                            saved_paths.append(path)
                        
                        img = Image.open(io.BytesIO(photo['data']))
                        image_np = np.array(img.convert("RGB"))
                        
                        detected, _, num_faces = predict_attendance(image_np, subject_id=subject_id)
                        
                        for s_id, present in detected.items():
                            if present:
                                detected_union[s_id] = True
                        total_faces += num_faces
                        
                    st.session_state['saved_disk_paths'] = saved_paths
                    st.session_state['detection_results'] = {
                        'detected': detected_union,
                        'num_faces': total_faces
                    }
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Error executing AI Attendance pipeline: {e}")

    # Display results
    if st.session_state.get('detection_results') is not None:
        results = st.session_state['detection_results']
        detected = results['detected']
        num_faces = results['num_faces']
        
        students = get_students_by_subject(subject_id)
        student_map = {s['student_id']: s for s in students}
        
        st.write("")
        st.markdown(f"### 📊 Scan Results (Detected {num_faces} total faces across all photos)")
        
        if not students:
            st.info("No registered students found in the database for this subject. Go to Student Portal to register student profiles first.")
            return
            
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
                try:
                    for item in attendance_list:
                        log_attendance(item['student_id'], subject_id, item['is_present'])
                    
                    for path in st.session_state.get('saved_disk_paths', []):
                        if os.path.exists(path):
                            try:
                                os.remove(path)
                            except Exception:
                                pass
                                
                    st.session_state['scanner_photos'] = []
                    st.session_state['detection_results'] = None
                    st.session_state['saved_disk_paths'] = []
                    
                    st.success(f"Attendance logged successfully for class '{selected_sub_label}'! All temporary images have been deleted.")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to log attendance: {e}")

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
        students = get_students_by_subject(subject_id)
        student_map = {s['student_id']: s['name'] for s in students}
        
    if not logs:
        st.info("No attendance logs found for this class.")
        return
        
    log_data = []
    present_logs = []
    
    # Sort logs by timestamp descending so latest is on top
    sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    for log in sorted_logs:
        if not log['is_present']:
            continue
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
            'Student ID': str(s_id), # Represent as string so table formats it without formatting
            'Student Name': s_name
        })
        present_logs.append(log)
        
    df_logs = pd.DataFrame(log_data)
    
    col_total, col_present_rate = st.columns(2)
    total_records = len(logs)
    present_records = len(present_logs)
    overall_rate = (present_records / total_records) * 100 if total_records else 0
    
    with col_total:
        st.metric("Total Records logged", total_records)
    with col_present_rate:
        st.metric("Overall Attendance Rate", f"{overall_rate:.1f}%")
        
    st.write("")
    
    # Construct Plain Text File report content
    report_lines = []
    report_lines.append("=========================================")
    report_lines.append("       SNAP ATTEND - PRESENT STUDENTS    ")
    report_lines.append("=========================================")
    report_lines.append(f"Class: {selected_sub_label}")
    report_lines.append(f"Total Present Records: {len(present_logs)}")
    report_lines.append("-----------------------------------------")
    report_lines.append(f"{'Timestamp':19} | {'Student ID':15} | {'Student Name'}")
    report_lines.append("-----------------------------------------")
    
    for entry in log_data:
        report_lines.append(f"{entry['Timestamp']:19} | {entry['Student ID']:15} | {entry['Student Name']}")
        
    report_text = "\n".join(report_lines)
    
    st.download_button(
        label="📥 Export Present Students as TXT",
        data=report_text,
        file_name=f"present_students_{subject_id}.txt",
        mime="text/plain",
        width="stretch"
    )
    
    st.write("")
    if not df_logs.empty:
        st.dataframe(df_logs, width="stretch", hide_index=True)
    else:
        st.info("No present records found in logs.")

    st.write("")
    with st.expander("🗑️ Delete & Manage Logs"):
        st.markdown("#### Delete Specific Logs")
        options = []
        option_to_id = {}
        for log in sorted_logs:
            s_id = log['student_id']
            s_name = student_map.get(s_id, f"Unknown Student (ID: {s_id})")
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(log['timestamp'].replace("Z", "+00:00"))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_time = log['timestamp']
            
            status_emoji = "✅ Present" if log['is_present'] else "❌ Absent"
            label = f"{formatted_time} - {s_name} (ID: {s_id}) [{status_emoji}]"
            options.append(label)
            option_to_id[label] = log['id']
            
        selected_labels = st.multiselect(
            "Select logs to delete:",
            options=options,
            key="delete_logs_multiselect"
        )
        
        if selected_labels:
            if st.button("🗑️ Delete Selected Logs", key="btn_delete_selected_logs", type="primary"):
                ids_to_delete = [option_to_id[lbl] for lbl in selected_labels]
                with st.spinner("Deleting selected logs..."):
                    try:
                        delete_attendance_logs(ids_to_delete)
                        st.success(f"Successfully deleted {len(ids_to_delete)} logs!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete logs: {e}")
                        
        st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
        st.markdown("#### Clear All Logs")
        st.warning("⚠️ Warning: This will permanently delete all attendance logs for this class.")
        confirm_clear = st.checkbox("I confirm that I want to delete all attendance logs for this class.", key="confirm_clear_all_logs")
        if st.button("🚨 Clear All Logs", key="btn_clear_all_logs", type="primary", disabled=not confirm_clear):
            with st.spinner("Clearing all logs for this class..."):
                try:
                    clear_attendance_logs_by_subject(subject_id)
                    st.success("Successfully deleted all attendance logs for this class!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear logs: {e}")

def render_auth_flow():
    _, col_form, _ = st.columns([1, 3.5, 1])

    with col_form:
        if st.session_state['teacher_mode'] == 'register':
            st.markdown('<h1 style="text-align: center; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 2.3rem; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 25px;">Register your teacher profile</h1>', unsafe_allow_html=True)
            
            with st.form("register_form", clear_on_submit=False):
                username = st.text_input("Enter username", placeholder="@abhishek", key="reg_username")
                name = st.text_input("Enter name", placeholder="Abhishek Sharma", key="reg_name")
                password = st.text_input("Enter password", type="password", placeholder="Enter your password", key="reg_password")
                confirm_password = st.text_input("Confirm password", type="password", placeholder="Confirm your password", key="reg_confirm_password")
                
                st.write("")
                submit_register = st.form_submit_button("👤+ Register Now", type="primary", use_container_width=True)
                
            if submit_register:
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
                        
            st.write("")
            if st.button("👤 Login instead", key="btn_login_instead", type="secondary", width="stretch"):
                st.session_state['teacher_mode'] = 'login'
                st.rerun()
                    
        else:
            st.markdown('<h1 style="text-align: center; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 2.3rem; font-weight: 800; color: #0E1428; margin-top: 15px; margin-bottom: 25px;">Login to your teacher profile</h1>', unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Enter username", placeholder="@abhishek", key="login_username")
                password = st.text_input("Enter password", type="password", placeholder="Enter your password", key="login_password")
                
                st.write("")
                submit_login = st.form_submit_button("🔑 Login Now", type="primary", use_container_width=True)
                
            if submit_login:
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
                        
            st.write("")
            if st.button("👤+ Register instead", key="btn_register_instead", type="secondary", width="stretch"):
                st.session_state['teacher_mode'] = 'register'
                st.rerun()

    # Footer Branding
    st.markdown("""
    <div class="footer-branding" style="margin-top: 60px;">
        Created with <span class="heart">❤️</span> by <span style="color: #F18805; font-weight: 700;">Jagan</span> <span style="color: #F0A202; font-weight: 700;">Ramadugu</span>
    </div>
    """, unsafe_allow_html=True)