"""
ATTENDX AI - Database Query Interface

This module provides an abstraction layer over the Supabase client, offering helper
functions for teacher authentication, student profile registration, class/subject
management, student enrollment, and attendance logging.
"""

import bcrypt
from src.database.config import supabase

def hash_pass(pwd):
    """
    Hashes a plaintext password using bcrypt.

    Args:
        pwd (str): Plaintext password to hash.

    Returns:
        str: Hashed password string.
    """
    return bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_pass(pwd, hashed):
    """
    Verifies a plaintext password against a stored bcrypt hash.

    Args:
        pwd (str): Plaintext password to check.
        hashed (str | bytes): Hashed password to verify against.

    Returns:
        bool: True if password matches, False otherwise.
    """
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(pwd.encode('utf-8'), hashed)

def check_teacher_exists(username):
    """
    Checks if a teacher username already exists in the database.

    Args:
        username (str): The teacher username to check.

    Returns:
        bool: True if the username exists, False otherwise.
    """
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0

def create_teacher(username, password, name):
    """
    Registers a new teacher profile in the database.

    Args:
        username (str): The unique login username.
        password (str): The plaintext password to hash and store.
        name (str): The teacher's display name.

    Returns:
        list: Inserted teacher record data.
    """
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username, password):
    """
    Authenticates a teacher login request.

    Args:
        username (str): Login username.
        password (str): Plaintext login password.

    Returns:
        dict | None: The teacher record dictionary if authentication succeeds, otherwise None.
    """
    response = supabase.table("teachers").select("*").eq('username', username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None

def get_all_students():
    """
    Retrieves all registered students in the database.

    Returns:
        list: A list of dictionaries representing all student records.
    """
    response = supabase.table('students').select('*').execute()
    return response.data

def check_student_exists(student_id):
    """
    Checks if a student profile exists for a given student ID.

    Args:
        student_id (int): Student unique ID.

    Returns:
        bool: True if the student exists, False otherwise.
    """
    response = supabase.table('students').select('student_id').eq('student_id', student_id).execute()
    return len(response.data) > 0

def get_student_by_id(student_id):
    """
    Retrieves student details by their unique student ID.

    Args:
        student_id (int): The unique student ID.

    Returns:
        dict | None: The student record dictionary if found, otherwise None.
    """
    response = supabase.table('students').select('*').eq('student_id', student_id).execute()
    if response.data:
        return response.data[0]
    return None

def create_student(student_id, name, face_embedding):
    """
    Registers a new student profile with their biometric face embedding vector.

    Args:
        student_id (int): Unique student identifier.
        name (str): Student's full name.
        face_embedding (list): 128-dimensional biometric embedding array.

    Returns:
        list: The created student record data.
    """
    data = {
        'student_id': student_id,
        'name': name,
        'face_embedding': face_embedding
    }
    response = supabase.table('students').insert(data).execute()
    return response.data

def create_subject(subject_code, name, section, teacher_id):
    """
    Creates a new subject class linked to a specific teacher.

    Args:
        subject_code (str): Course code (e.g. CS-101).
        name (str): Course display name.
        section (str): Class section identifier.
        teacher_id (int): ID of the teacher managing the course.

    Returns:
        list: Created subject record data.
    """
    data = {
        'subject_code': subject_code,
        'name': name,
        'section': section,
        'teacher_id': teacher_id
    }
    response = supabase.table('subjects').insert(data).execute()
    return response.data

def get_subjects_by_teacher(teacher_id):
    """
    Gets all subjects managed by a specific teacher.

    Args:
        teacher_id (int): Unique teacher identifier.

    Returns:
        list: List of subjects managed by the teacher.
    """
    response = supabase.table('subjects').select('*').eq('teacher_id', teacher_id).execute()
    return response.data

def log_attendance(student_id, subject_id, is_present=True):
    """
    Creates an attendance log record for a student in a specific course.

    Args:
        student_id (int): The student's ID.
        subject_id (int): The subject's course ID.
        is_present (bool): Student presence status (defaults to True).

    Returns:
        list: Created attendance log record.
    """
    data = {
        'student_id': student_id,
        'subject_id': subject_id,
        'is_present': is_present
    }
    response = supabase.table('attendance_logs').insert(data).execute()
    return response.data

def get_attendance_reports(subject_id):
    """
    Retrieves all attendance logs recorded for a specific subject.

    Args:
        subject_id (int): The course ID to fetch reports for.

    Returns:
        list: List of attendance log dictionaries.
    """
    response = supabase.table('attendance_logs').select('*').eq('subject_id', subject_id).execute()
    return response.data

def delete_attendance_logs(log_ids):
    """
    Deletes specific attendance records by their database log IDs.

    Args:
        log_ids (list): List of log record IDs to delete.

    Returns:
        list: Response containing details of deleted records.
    """
    response = supabase.table('attendance_logs').delete().in_('id', log_ids).execute()
    return response.data

def clear_attendance_logs_by_subject(subject_id):
    """
    Clears all attendance history logs for a specific subject.

    Args:
        subject_id (int): Course ID to wipe attendance for.

    Returns:
        list: Response containing details of deleted records.
    """
    response = supabase.table('attendance_logs').delete().eq('subject_id', subject_id).execute()
    return response.data

def get_subject_by_id(subject_id):
    """
    Retrieves class details for a subject by its unique ID.

    Args:
        subject_id (int): Unique subject course ID.

    Returns:
        dict | None: The subject record dictionary if found, otherwise None.
    """
    response = supabase.table('subjects').select('*').eq('subject_id', subject_id).execute()
    if response.data:
        return response.data[0]
    return None

def enroll_student_in_subject(student_id, subject_id):
    """
    Enrolls a student in a subject class.

    Args:
        student_id (int): Student unique ID.
        subject_id (int): Subject course ID.

    Returns:
        list: The created enrollment record.
    """
    data = {
        'student_id': student_id,
        'subject_id': subject_id
    }
    response = supabase.table('subject_students').insert(data).execute()
    return response.data

def is_student_enrolled(student_id, subject_id):
    """
    Verifies if a student is enrolled in a specific subject.

    Args:
        student_id (int): Student unique ID.
        subject_id (int): Subject course ID.

    Returns:
        bool: True if enrolled, False otherwise.
    """
    response = supabase.table('subject_students').select('*').eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return len(response.data) > 0

def get_students_by_subject(subject_id):
    """
    Retrieves all enrolled students in a specific subject course.

    Args:
        subject_id (int): Subject course ID.

    Returns:
        list: A list of student records enrolled in the subject.
    """
    response = supabase.table('subject_students').select('student_id, students(*)').eq('subject_id', subject_id).execute()
    students = []
    for item in response.data:
        if item.get('students'):
            students.append(item['students'])
    return students

def delete_subject(subject_id):
    """
    Deletes a subject class and cascade-wipes related attendance logs and student enrollments.

    Args:
        subject_id (int): Course ID to delete.

    Returns:
        list: Details of the deleted subject record.
    """
    # 1. Delete dependent attendance logs
    supabase.table('attendance_logs').delete().eq('subject_id', subject_id).execute()
    # 2. Delete dependent student enrollments
    supabase.table('subject_students').delete().eq('subject_id', subject_id).execute()
    # 3. Delete the subject itself
    response = supabase.table('subjects').delete().eq('subject_id', subject_id).execute()
    return response.data





