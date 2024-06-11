import os
import docx
import spacy
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")

# Load Sentence Transformer model
sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to read resume files from a folder
def read_resume_files(folder_path):
    resumes = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.docx'):
            file_path = os.path.join(folder_path, filename)
            resume_text = read_docx(file_path)
            resumes.append({"name": os.path.splitext(filename)[0], "resume_text": resume_text})
    return resumes

# Function to read text from a docx file
def read_docx(file_path):
    doc = docx.Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

# Placeholder function for NER
def resume_analyzer(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ["SKILL", "QUALIFICATION"]:
            entities.append({"word": ent.text, "entity": ent.label_})
    return entities

# Function to analyze resumes and select top candidates
def analyze_resumes(resumes, job_description):
    # Perform analysis for each resume
    for resume in resumes:
        resume_text = resume['resume_text']
        # Perform NER on the resume
        resume_info = resume_analyzer(resume_text)

        # Extract skills and qualifications from the resume
        skills = [entity['word'] for entity in resume_info if entity['entity'] == 'SKILL']
        qualifications = [entity['word'] for entity in resume_info if entity['entity'] == 'QUALIFICATION']

        # Calculate similarity score between job description and resume
        resume_embedding = sentence_transformer_model.encode(resume_text)
        job_description_embedding = sentence_transformer_model.encode(job_description)
        similarity_score = cosine_similarity(job_description_embedding.reshape(1, -1), resume_embedding.reshape(1, -1))[0][0]

        # Add similarity score to the resume
        resume['similarity_score'] = similarity_score

    # Sort resumes by similarity score
    sorted_resumes = sorted(resumes, key=lambda x: x['similarity_score'], reverse=True)

    # Select top candidates
    top_candidates = [resume['name'] for resume in sorted_resumes[:10]]

    return top_candidates

# Streamlit app


import os
import streamlit as st
from datetime import datetime
import docx2txt

def read_docx(file):
    # Read text from a DOCX file
    return docx2txt.process(file)

def analyze_resumes(resumes, job_description):
    # Placeholder function to analyze resumes against the job description
    # Implement this function to analyze and rank resumes
    return [resume['name'] for resume in resumes][:5]

def read_resume_files(folder_path):
    # Placeholder function to read resumes from a folder
    # Implement this function to read and extract text from resume files in a folder
    return [
        {"name": "Sample Resume", "resume_text": "Sample resume text from folder", "contact": "1234567890", "address": "123 Sample St"}
    ]

def store_input_data(job_description, folder_path, uploaded_files):
    # Create a folder to store input data if it doesn't exist
    storage_folder = "input_data"
    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)
    
    # Store job description
    with open(os.path.join(storage_folder, "job_description.txt"), "w") as f:
        f.write(job_description)
    
    # Store folder path
    with open(os.path.join(storage_folder, "folder_path.txt"), "w") as f:
        f.write(folder_path)
    
    # Store uploaded files and extract candidate details
    candidate_details = []
    if uploaded_files:
        resumes_folder = os.path.join(storage_folder, "resumes")
        if not os.path.exists(resumes_folder):
            os.makedirs(resumes_folder)
        
        for file in uploaded_files:
            file_path = os.path.join(resumes_folder, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            resume_text = read_docx(file)
            # Placeholder for extracting candidate details from resume
            candidate_name = file.name.split('.')[0]  # Assuming the file name is the candidate's name
            candidate_contact = "Unknown"  # Placeholder for contact extraction logic
            candidate_address = "Unknown"  # Placeholder for address extraction logic
            candidate_details.append({
                "name": candidate_name,
                "contact": candidate_contact,
                "address": candidate_address,
                "resume_text": resume_text
            })
    
    # Store candidate details
    with open(os.path.join(storage_folder, "candidate_details.txt"), "w") as f:
        for detail in candidate_details:
            f.write(f"Name: {detail['name']}, Contact: {detail['contact']}, Address: {detail['address']}\n")
    
    return candidate_details

def main():
    st.set_page_config(page_title="Automated Resume Review System", page_icon=":memo:", layout="wide")

    # Embedded CSS for styling
    st.markdown(
        """
        <style>
        header {
            background-color: #4CAF50;
            padding: 24px;
            text-align: center;
            font-size: 40px;
            color: white;
        }
        footer {
            background-color: #f1f1f1;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            color: #333;
        }
        .stTextArea, .stTextInput, .stFileUploader, .stButton {
            margin-bottom: 20px;
        }
        .separator {
            text-align: center;
            margin: 20px 0;
        }
        .separator::before {
            content: "or";
            display: inline-block;
            background: white;
            padding: 0 10px;
            color: #555;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown('<header>Welcome to the Automated Resume Review System</header>', unsafe_allow_html=True)
    st.markdown("## Resume Analyzer")
    st.markdown("#### Developed by Irfan Khattak")
    st.write("Please provide the necessary details below to analyze resumes.")
    
    with st.form(key='resume_form'):
        # Job description input
        job_description = st.text_area("Enter the job description:", 
            "We are looking for a Python developer with experience in Django and Flask frameworks.")
        # Folder path input
        folder_path = st.text_input("Enter the folder path for resumes:", value=r'C:\Users\irfan\Resumes')

        # Separator with "or"
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

        # File uploader for resumes
        uploaded_files = st.file_uploader("Upload resumes:", accept_multiple_files=True)
  
        # Submit button
        submit_button = st.form_submit_button(label="Analyze Resumes")
    
    if submit_button:
        candidate_details = store_input_data(job_description, folder_path, uploaded_files)
        if uploaded_files:
            with st.spinner("Reading and analyzing resumes..."):
                resumes = [{"name": detail['name'], "resume_text": detail['resume_text'], "contact": detail['contact'], "address": detail['address']} for detail in candidate_details]
                top_candidates = analyze_resumes(resumes, job_description)
                st.success("Analysis complete!")
                st.subheader("Top candidates for the job:")
                for candidate in top_candidates:
                    st.write(f"- {candidate}")
        elif folder_path:
            with st.spinner("Reading and analyzing resumes from folder..."):
                resumes = read_resume_files(folder_path)
                top_candidates = analyze_resumes(resumes, job_description)
                st.success("Analysis complete!")
                st.subheader("Top candidates for the job:")
                for candidate in top_candidates:
                    st.write(f"- {candidate}")
        else:
            st.error("Please provide a folder path or upload at least one resume.")

    st.markdown('<footer>© 2024 Irfan Khattak. All rights reserved.</footer>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
