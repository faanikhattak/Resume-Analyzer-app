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

def main():
    st.set_page_config(page_title="Automated Resume Review System", page_icon=":memo:", layout="centered")

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
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown('<header>Automated Resume Review System: Resume Analyzer</header>', unsafe_allow_html=True)
    
    st.markdown("#### Developed by Irfan Khattak")
    st.write("Welcome to the Automated Resume Review System. Please provide the necessary details below to analyze resumes.")
    
    with st.form(key='resume_form'):
        # Job description input
        job_description = st.text_area("Enter the job description:", 
            "We are looking for a Python developer with experience in Django and Flask frameworks.")
        # Folder path input
        folder_path = st.text_input("Enter the folder path for resumes:", value=r'C:\Users\irfan\Resumes')

        # Separator with "or"
        st.markdown('<div class="separator">or</div>', unsafe_allow_html=True)

        # File uploader for resumes
        uploaded_files = st.file_uploader("Upload resumes:", accept_multiple_files=True)
  
        # Submit button
        submit_button = st.form_submit_button(label="Analyze Resumes")
    
    if submit_button:
        if uploaded_files:
            with st.spinner("Reading and analyzing resumes..."):
                resumes = [{"name": file.name, "resume_text": read_docx(file)} for file in uploaded_files]
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
