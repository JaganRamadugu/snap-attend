import bcrypt
from src.database.config import supabase

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_pass(pwd, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(pwd.encode('utf-8'), hashed)

def check_teacher_exists(username):
    # check for the unique username for teacher
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0

def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq('username', username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None

def get_all_students():
    response = supabase.table('students').select('*').execute()
    return response.data

def check_student_exists(student_id):
    response = supabase.table('students').select('student_id').eq('student_id', student_id).execute()
    return len(response.data) > 0

def get_student_by_id(student_id):
    response = supabase.table('students').select('*').eq('student_id', student_id).execute()
    if response.data:
        return response.data[0]
    return None

def create_student(student_id, name, face_embedding):
    data = {
        'student_id': student_id,
        'name': name,
        'face_embedding': face_embedding
    }
    response = supabase.table('students').insert(data).execute()
    return response.data

def create_subject(subject_code, name, section, teacher_id):
    data = {
        'subject_code': subject_code,
        'name': name,
        'section': section,
        'teacher_id': teacher_id
    }
    response = supabase.table('subjects').insert(data).execute()
    return response.data

def get_subjects_by_teacher(teacher_id):
    response = supabase.table('subjects').select('*').eq('teacher_id', teacher_id).execute()
    return response.data

def log_attendance(student_id, subject_id, is_present=True):
    data = {
        'student_id': student_id,
        'subject_id': subject_id,
        'is_present': is_present
    }
    response = supabase.table('attendance_logs').insert(data).execute()
    return response.data

def get_attendance_reports(subject_id):
    response = supabase.table('attendance_logs').select('*').eq('subject_id', subject_id).execute()
    return response.data

def delete_attendance_logs(log_ids):
    response = supabase.table('attendance_logs').delete().in_('id', log_ids).execute()
    return response.data

def clear_attendance_logs_by_subject(subject_id):
    response = supabase.table('attendance_logs').delete().eq('subject_id', subject_id).execute()
    return response.data

def get_subject_by_id(subject_id):
    response = supabase.table('subjects').select('*').eq('subject_id', subject_id).execute()
    if response.data:
        return response.data[0]
    return None

def enroll_student_in_subject(student_id, subject_id):
    data = {
        'student_id': student_id,
        'subject_id': subject_id
    }
    response = supabase.table('subject_students').insert(data).execute()
    return response.data

def is_student_enrolled(student_id, subject_id):
    response = supabase.table('subject_students').select('*').eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return len(response.data) > 0

def get_students_by_subject(subject_id):
    response = supabase.table('subject_students').select('student_id, students(*)').eq('subject_id', subject_id).execute()
    students = []
    for item in response.data:
        if item.get('students'):
            students.append(item['students'])
    return students



