import streamlit as st 

def style_background_home():
    st.markdown("""
                <style>
                .stApp {
                    background: #5865F2 !important; 
                }
                .stApp div[data-testid="stColumn"]{
                    background-color:#E0E3FF !important;
                    padding:1.5 rem !important;
                    border-radius:5rem !important;                   
                }
                </style>
                """, unsafe_allow_html=True)
    
def style_background_dashboard():
    st.markdown("""
                <style>
                .stApp {
                    background: #E0E3FF !important;
                }
                </style>
                """, unsafe_allow_html=True)

def style_base_layout():
    st.markdown("""
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');
                
                /*Hide Top Toolbar of Streamlit*/
                #MainMenu, footer, header {
                    visibility: hidden;
                }
                .block-container {
                    padding-top: 1.5rem !important;
                }
                h1 {
                    font-family: 'Climate Crisis', sans-serif !important;
                    font-size: 3.5rem !important;
                    line-height: 1.1 !important;
                    margin-bottom: 0rem !important;
                }
                h2 {
                    font-family: 'Climate Crisis', sans-serif !important;
                    font-size: 1.5rem !important; /* Reduced from 2rem to prevent overlapping */
                    line-height: 1.2 !important;  /* Added breathing room between lines */
                    margin-bottom: 1rem !important;
                    color: black !important; /* Makes 'I'm Student' and 'I'm Teacher' black */
                } 
                h3, h4, p {
                    font-family: 'Outfit', sans-serif;  
                }
                
                /* Base Button Styling */
                div.stButton button {
                    border-radius: 1.5rem !important;
                    background-color: #5865F2 !important;
                    color: white !important;
                    padding: 10px 20px !important;
                    border: none !important;
                    transition: transform 0.25s ease-in-out !important;
                }
                
                /* Secondary Button Styling */
                div.stButton button[kind="secondary"], div.stButton button[kind="Secondary"] {
                    background-color: #EB459E !important;
                    color: white !important;
                }
                
                /* Tertiary Button Styling */
                div.stButton button[kind="tertiary"] {
                    background-color: black !important;
                    color: white !important;
                } 
                
                /* Hover Effect */
                div.stButton button:hover {
                    transform: scale(1.05) !important;
                }
                </style>
                """, unsafe_allow_html=True)