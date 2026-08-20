"""
ATTENDX AI - Facial Recognition Pipeline

This module implements the biometric face detection and recognition pipeline.
It utilizes the Dlib library for face detection and landmark prediction, maps faces
to a 128-dimensional vector space, and identifies students using minimum Euclidean
distance classification.
"""

import dlib
import numpy as np
import face_recognition_models
from face_recognition_models import face_recognition_model_location
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students, get_students_by_subject

@st.cache_resource
def load_dlib_models():
    """
    Loads and caches the Dlib frontal face detector, 5-point shape predictor,
    and the resnet face recognition model. Caching ensures models are only loaded once
    into memory across multiple user sessions.

    Returns:
        tuple: (detector, shape_predictor, face_recognition_model)
    """
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_model_location()
    )

    return detector, sp, facerec

def get_face_embeddings(image_np):
    """
    Extracts 128-dimensional facial embeddings for all detected faces in a raw image.

    Args:
        image_np (numpy.ndarray): 3-channel RGB image matrix.

    Returns:
        list: A list of numpy arrays, each representing a 128-d face embedding vector.
    """
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)

    encodings = []

    for face in faces:
        # Predict 5-point face landmarks (eyes, nose, mouth corners)
        shape = sp(image_np, face)
        # Compute the 128-dimensional face descriptor vector
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)
        
        encodings.append(np.array(face_descriptor))
    return encodings

@st.cache_resource
def get_trained_model():
    """
    Trains and caches an SVM classifier on the entire student database.
    This acts as a secondary classifier if multi-class classification is required.

    Returns:
        dict | None: Dictionary containing the trained SVC model, features list (X),
                     and labels list (y) if database is populated, otherwise None.
    """
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

    # Fit a Support Vector Classifier with a linear kernel and balanced class weights
    clf = SVC(kernel='linear', probability=True, class_weight='balanced')

    if len(set(y)) >= 2:
        try:
            clf.fit(X, y)
        except ValueError:
            pass
            
    return {'clf': clf, 'X': X, 'y': y}

def train_classifier():
    """
    Clears the cached SVM model and retrains it from scratch with the latest database records.

    Returns:
        bool: True if training succeeded, False otherwise.
    """
    get_trained_model.clear()
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np, subject_id=None):
    """
    Processes a group/class image and identifies students using minimum Euclidean distance
    comparison against enrolled student profiles.

    Args:
        class_image_np (numpy.ndarray): RGB image of the classroom.
        subject_id (int | None): ID of the subject to restrict search to. If None,
                                 compares against all students in the database.

    Returns:
        tuple: (detected_student_dict, all_subject_students_list, number_of_detected_faces_int)
    """
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    # Narrow down comparison list (X, y) based on subject enrollment
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

    # Process each detected face vector in the query image
    for encoding in encodings:
        best_match_id = None
        min_dist = float('inf')

        # Compare face encoding with registered student embedding using Euclidean distance (L2 norm)
        for idx, student_emb in enumerate(X):
            dist = np.linalg.norm(student_emb - encoding)
            if dist < min_dist:
                min_dist = dist
                best_match_id = y[idx]

        # Resemblance threshold (0.6 is typical for dlib distance metrics)
        resemblance_threshold = 0.6

        if min_dist <= resemblance_threshold and best_match_id is not None:
            detected_student[best_match_id] = True

    return detected_student, all_students, len(encodings)