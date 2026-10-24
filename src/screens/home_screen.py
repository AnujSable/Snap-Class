import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_dashboard, style_background_home

def home_screen(): 
    header_home()
    style_background_home()
    style_base_layout() # Inject style tag
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.header("I'm Student")
        st.image("https://i.ibb.co/844D9Lrt/mascot-student.png", width=120)
        if st.button('Student Portal ↗', type="primary", key="student_btn"):
            st.session_state['login_type'] = 'student'
            st.rerun() 
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
        st.header("I'm Teacher")
        st.image("https://i.ibb.co/844D9Lrt/mascot-prof.png", width=145)
        if st.button('Teacher Portal ↗', type="primary", key="teacher_btn"):
            st.session_state['login_type'] = 'teacher'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
    footer_home()