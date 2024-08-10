import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Smart ATS",
    page_icon="👨‍💼",
    layout="centered",
)

# Fixed Google API Key
API_KEY = "AIzaSyDctparXTyoOMch-FduR4gV-VM82JGHgCM"

# Function to configure Gemini AI model with the provided API key
def configure_gemini_api(api_key):
    genai.configure(api_key=api_key)

# Configure Gemini AI model with the provided API key
configure_gemini_api(API_KEY)

# Function to get response from Gemini AI
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from uploaded PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Function to get interview questions and answers from Gemini AI
def get_interview_qa(jd, num_questions=10):
    qa_prompt = f"""
    Create {num_questions} interview questions and answers based on the following job description:
    {jd}
    """
    response = get_gemini_response(qa_prompt)
    return response

# Function to get job roles from Gemini AI
def get_job_roles(jd):
    roles_prompt = f"""
    Based on the following job description, generate a list of related job roles:
    {jd}
    """
    response = get_gemini_response(roles_prompt)
    return response

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analyst
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide the 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        background-color: #680303;
        color: #940505;
    }
    .stTextInput, .stTextArea, .stButton, .stFileUploader {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #d1d5db;
        border-radius: 5px;
        padding: 10px;
    }
    .stTextInput input, .stTextArea textarea, .stFileUploader input {
        background-color: #ffffff;
        color: #000000;
    }
    .stButton button {
        background-color: #007bff;
        color: #ffffff;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    .stSidebar {
        background-color: #28334AFF;
        color: #FFFFFF;
    }
    .stSidebar .sidebar-content {
        color: #FFFFFF;
    }
    .stSidebar .sidebar-content .block-container h1 {
        color: #FFFFFF;
    }
    .response-text {
        color: #000000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

## Streamlit app
st.sidebar.title("Menu")
menu = st.sidebar.selectbox("Select a section", ["Job Description & Upload Resume", "Job Roles", "Interview Q&A"])

st.title("Resume Matcher ATS")

# Use Streamlit session state to store job description
if "jd" not in st.session_state:
    st.session_state.jd = ""

if menu == "Job Description & Upload Resume":
    st.session_state.jd = st.text_area("Paste the Job Description")
    
    uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")
    submit = st.button("Submit")

    if submit:
        if uploaded_file is not None:
            text = input_pdf_text(uploaded_file)
            response = get_gemini_response(input_prompt.format(text=text, jd=st.session_state.jd))
            st.subheader("Response:")
            parsed_response = json.loads(response)
            st.markdown(f"<div class='response-text'>{json.dumps(parsed_response, indent=4)}</div>", unsafe_allow_html=True)

elif menu == "Job Roles":
    st.subheader("Related Job Roles")
    if st.session_state.jd:
        roles_response = get_job_roles(st.session_state.jd)
        st.markdown(f"<div class='response-text'>{roles_response}</div>", unsafe_allow_html=True)
    else:
        st.error("Please enter a job description in the 'Job Description & Upload Resume' section.")

elif menu == "Interview Q&A":
    st.subheader("Interview Questions and Answers")
    if st.session_state.jd:
        if "num_questions" not in st.session_state:
            st.session_state.num_questions = 10
        
        qa_response = get_interview_qa(st.session_state.jd, st.session_state.num_questions)
        st.markdown(f"<div class='response-text'>{qa_response}</div>", unsafe_allow_html=True)
        
        if st.button("More"):
            st.session_state.num_questions += 10
            qa_response = get_interview_qa(st.session_state.jd, st.session_state.num_questions)
            st.markdown(f"<div class='response-text'>{qa_response}</div>", unsafe_allow_html=True)
    else:
        st.error("Please enter a job description in the 'Job Description & Upload Resume' section.")
