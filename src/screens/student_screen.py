import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
from src.components.subject_card import subject_card
from src.components.dialog_enroll import enroll_dialog
import numpy as np 
from src.pipelines.face_pipeline import predict_attendance, get_face_embedding, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendence, unenroll_student_to_subject
import time


def student_dashboard():
    student_data = st.session_state.student_data 
    student_id=student_data['student_id']
    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}")
        if st.button('Logout', type='secondary', key='loginbackbtn', shortcut="ctrl+backspace"):
            st.session_state['is_logged_in'] = False  # Fixed key name
            if 'student_data' in st.session_state:
                del st.session_state['student_data']
            st.rerun()
    st.space()
    c1,c2=st.columns(2)
    with c1:
        st.header("Your Enrolled Subjects")
    with c2:
        if st.button("Enroll in Subject",type='primary',width='stretch'):
            enroll_dialog()
            
    st.divider()
    with st.spinner('Loading your enrolled subjects...'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendence(student_id)
    
    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    cols = st.columns(2)
    
    # Define the unenroll callback outside the loop to avoid duplicate ID issues
    def make_unenroll_callback(s_id, s_name):
        def callback():
            if st.button(f"Unenroll from {s_name}", type='tertiary', width='stretch', key=f"unenroll_{s_id}"):
                unenroll_student_to_subject(student_id, s_id)
                st.toast(f"Unenrolled from {s_name} successfully!")
                st.rerun()
        return callback

    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        stats = stats_map.get(sid, {'total': 0, "attended": 0})
        
        # Fallback to subject_name if name is missing
        sub_name = sub.get('subject_name') or sub.get('name') or 'Unnamed Subject'
        
        with cols[i % 2]:
            subject_card(
                name=sub_name,
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ("📊", str(stats['total']), "Total"),
                    ("✅", str(stats['attended']), "Attended"),
                ],
                footer_callback=make_unenroll_callback(sid, sub_name) 
            )
    
    
        
    footer_dashboard() 

def student_screen():
    style_background_dashboard()
    style_base_layout()
    
    if 'student_data' in st.session_state:
        student_dashboard()
        return 
    
    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
            header_dashboard()
    with c2:
            if st.button('Go back to Home', type='secondary', key='loginbackbtn', shortcut="ctrl+backspace"):
                st.session_state['login_type'] = None
                st.rerun()
                
    st.header("Login using FaceID",text_alignment='center')
    st.space()
    st.space()
    show_registration=False
    
    photo_source=st.camera_input("Position your face in the center")
    
    if photo_source:#if photo clicked
        img=np.array(Image.open(photo_source))#image.open library for images
        with st.spinner('AI is scanning...'):#it will not show until the process is completed
            detected,all_ids,num_faces = predict_attendance(img)
            if num_faces==0:
                st.warning("Face not found!")
            elif num_faces>1:
                st.warning("Multiple faces detected!")
            else:
                if detected:
                    student_id=list(detected.keys())[0]#it gives the first student id from the detected dictionary keys
                    all_students=get_all_students()#get the ids of all students
                    student=next((s for s in all_students if s['student_id']==student_id),None)#this loop tells that
                    
                    if student:
                        st.session_state.is_logged_in = True # tells all session to be logged in(true)
                        st.session_state.user_role='student'
                        st.session_state.student_data=student 
                        st.toast(f'Welcome {student["name"]}')
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Face not recognized!You might be a new student!")
                    show_registration=True
    if show_registration:
        with st.container(border=True):
            st.header("Register as a new student")
            new_name=st.text_input("Enter your name")
            email=st.text_input("Enter your email")
            st.subheader("Optional : Voice Enrollment")
            st.info('Enroll your for voice only attendence')
            audio_data=None
            try:
                audio_data=st.audio_input("Record your voice")
            except Exception:
                st.error('Audio data failed')
            if st.button("Create Account",type='primary'):
                if new_name:
                    with st.spinner("Creating profile..."):
                        img= np.array(Image.open(photo_source))
                        encoding=get_face_embedding(img)
                        if encoding:
                            face_emb=encoding[0].tolist()
                            voice_emb=None
                            if audio_data:
                                voice_emb=get_voice_embedding(audio_data.read())
                                
                            response_data=create_student(new_name,face_embedding=face_emb,voice_embedding=voice_emb)
                            
                            if response_data:
                                train_classifier() #clear previous cache and train the model with new student data and store in cache
                                st.session_state.is_logged_in = True
                                st.session_state.user_role='student'
                                st.session_state.student_data=response_data[0]
                                st.toast(f'Profile Created! Welcome {new_name}')
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to create profile!")
                else:
                    st.warning("Please enter your name!")
                    
                    
                                        
    footer_dashboard()