from src.database.config import supabase
import bcrypt

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def check_teacher_exists(username):
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0

def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data 

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None

def get_all_students():
    response = supabase.table('students').select("*").execute()
    return response.data

def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {'name': new_name, 'face_embedding': face_embedding, 'voice_embedding': voice_embedding}
    response = supabase.table('students').insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = supabase.table("subjects").select("*").eq("teacher_id", teacher_id).execute()
    subjects = response.data if response.data else []
    
    for sub in subjects:
        sub_id = sub.get('id') or sub.get('subject_id')
        try:
            # Must be plural 'subject_students'
            students_resp = supabase.table("subject_students").select("*", count="exact", head=True).eq("subject_id", sub_id).execute()
            sub['total_students'] = students_resp.count if hasattr(students_resp, 'count') else 0
        except Exception:
            sub['total_students'] = 0
            
        try:
            logs_resp = supabase.table("attendance_logs").select("timestamp").eq("subject_id", sub_id).execute()
            attendance = logs_resp.data if logs_resp.data else []
            unique_sessions = len(set(log['timestamp'] for log in attendance if 'timestamp' in log))
            sub['total_sessions'] = unique_sessions
        except Exception:
            sub['total_sessions'] = 0
            
    return subjects

def create_subject(subject_code, subject_name, section, teacher_id):
    data = {
        "subject_code": subject_code,
        "subject_name": subject_name,
        "section": section,
        "teacher_id": teacher_id
    }
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def unenroll_student_to_subject(student_id, subject_id):
    response = supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()  
    return response.data

def enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response = supabase.table('subject_students').insert(data).execute()# Corrected to plural
    return response.data

def get_student_subjects(student_id):
    response = supabase.table('subject_students').select('*,subjects(*)').eq('student_id', student_id).execute()
    return response.data

def get_student_attendence(student_id):
    response = supabase.table('attendance_logs').select('*,subjects(*)').eq('student_id', student_id).execute()
    return response.data

def create_attendance(logs):
    response=supabase.table('attendance_logs').insert(logs).execute()
    return response.data

def get_attendance_for_teacher(teacher_id):
    # Fixed syntax: use !inner instead of (inner(*))
    response = supabase.table('attendance_logs').select('*, subjects!inner(*)').eq('subjects.teacher_id', teacher_id).execute()
    return response.data