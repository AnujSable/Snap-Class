# Face Image
#     |
# Face Detector (dlib)
#     |
# Shape Predictor(sp)-> landmarks
#     |
# ResNet (facerec) -> embedding (128D)
 
import dlib
import numpy as np 
import face_recognition_models 
from sklearn.svm import SVC #classify images 
import streamlit as st 
from src.database.db import get_all_students # get all facees of students from db


@st.cache_resource#load only one time
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()#It is used to scan an image and locate the bounding boxes (coordinates) of human faces that are facing directly or nearly directly toward the camera
    sp=dlib.shape_predictor(#initializes a dlib facial landmark detector by loading a pre-trained machine learning model that locates specific points on a human face.
        face_recognition_models.pose_predictor_model_location() 
    )
    
    facerec=dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )
    
    return detector,sp,facerec

def get_face_embedding(image_np):
    detector,sp,facerec= load_dlib_models()
    faces=detector(image_np,1)
    encodings=[] #
    for face in faces:  #
        shape=sp(image_np,face)
        face_descriptor=facerec.compute_face_descriptor(image_np,shape,1)#128 embedding
        encodings.append(np.array(face_descriptor))
    return encodings        

@st.cache_data #used coz not need of this function to be called again and again
def get_trained_model():#fit images in model svm takes image and tell where it is
    X=[] #student face embeddings
    y=[] #ids
    
    student_db=get_all_students()
    if not student_db:
        return None
    
    for student in student_db:
        embedding =student.get('face_embedding')#all student embeding
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))
            
    if len(X)==0: #if embedding not found for any student
        return 0 
    clf=SVC(kernel='linear',probability=True,class_weight='balanced')
    
    try:
        clf.fit(X,y)
    except ValueError:
        pass
    return {'clf':clf,'X':X,'y':y}
    
def train_classifier():#make new data store in cache
    st.cache_resource.clear()#clear previous cache
    model_data=get_trained_model()#new student data will be stored in cache
    return bool(model_data)

def predict_attendance(class_image_np):
    encodings = get_face_embedding(class_image_np)  # make the embeddings of the image
    detected_student = {}
    model_data = get_trained_model()
    if not model_data:
        return detected_student, [], len(encodings)
    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train))) 
    for encoding in encodings:
        if len(all_students) >= 2:  # if more than 2 students in db
            predicted_id = int(clf.predict([encoding])[0])  # gives the predicted id of the student in the image
        else:  # if only one student in db
            predicted_id = int(all_students[0])  # only one student in db so predicted id will be that student id
    
        student_embedding = X_train[y_train.index(predicted_id)]  # gives the embedding of the student in db with predicted id
    
        best_match_score = np.linalg.norm(student_embedding - encoding)  # Fixed variable name
        resemblance_threshold = 0.6  # tells that if the best match score is less than 0.6 then it is a match otherwise not
    
        if best_match_score <= resemblance_threshold:
            detected_student[predicted_id] = True
    
    return detected_student, all_students, len(encodings)  # Fixed pluralization variable