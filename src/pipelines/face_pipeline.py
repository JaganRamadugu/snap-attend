import dlib
import numpy as np
import face_recognition_models
from face_recognition_models import face_recognition_model_location
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students, get_students_by_subject

@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_model_location()
    )

    return detector, sp, facerec

def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)

    encodings = []

    for face in faces:
        shape = sp(image_np,face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape,1)
        
        encodings.append(np.array(face_descriptor))
    return encodings

@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))
        
    if len(X) == 0:
        return None

    clf = SVC(kernel='linear', probability=True, class_weight='balanced')

    if len(set(y)) >= 2:
        try:
            clf.fit(X, y)
        except ValueError:
            pass
            
    return {'clf': clf, 'X': X, 'y': y}

def train_classifier():
    get_trained_model.clear()
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np, subject_id=None):
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    if subject_id is not None:
        students = get_students_by_subject(subject_id)
        X = []
        y = []
        for student in students:
            embedding = student.get('face_embedding')
            if embedding:
                X.append(np.array(embedding))
                y.append(student.get('student_id'))
    else:
        model_data = get_trained_model()
        if not model_data:
            return detected_student, [], len(encodings)
        X = model_data['X']
        y = model_data['y']

    if not X:
        return detected_student, [], len(encodings)

    all_students = sorted(list(set(y)))

    for encoding in encodings:
        best_match_id = None
        min_dist = float('inf')

        # Compare this face encoding with every registered student embedding
        for idx, student_emb in enumerate(X):
            dist = np.linalg.norm(student_emb - encoding)
            if dist < min_dist:
                min_dist = dist
                best_match_id = y[idx]

        resemblance_threshold = 0.6

        if min_dist <= resemblance_threshold and best_match_id is not None:
            detected_student[best_match_id] = True

    return detected_student, all_students, len(encodings)