import PyPDF2
import re
import json
import spacy
from io import BytesIO

nlp = spacy.load('en_core_web_sm')

def extract_text(file_data, file_type='pdf'):
    if file_type == 'pdf':
        return extract_text_from_pdf(file_data)
    else:
        raise ValueError("Unsupported file format")

def extract_text_from_pdf(binary_data):
    with BytesIO(binary_data) as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def extract_name_pattern(text):
    match = re.search(r'(?i)Name[:\s]+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)', text)
    if match:
        return match.group(1).strip()
    return "Name not found"

def extract_name_header(text):
    personal_info_text = extract_section(text, r'CONTACT INFORMATION|PERSONAL DETAILS', r'EDUCATION|SKILLS|EXPERIENCE')
    lines = personal_info_text.split('\n')
    for line in lines:
        if 'Name:' in line:
            return line.split('Name:')[1].strip()
    return "Name not found"

def extract_name_ner(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return "Name not found"

def extract_name_combined(text):
    name = extract_name_pattern(text)
    if name == "Name not found":
        name = extract_name_ner(text)
    if name == "Name not found":
        name = extract_name_header(text)
    return name

def extract_section(text, section_name, next_section_name=None):
    section_start = re.search(section_name, text, re.IGNORECASE)
    if section_start:
        if next_section_name:
            next_section_start = re.search(next_section_name, text[section_start.end():], re.IGNORECASE)
            if next_section_start:
                return text[section_start.end():section_start.end() + next_section_start.start()].strip()
        return text[section_start.end():].strip()
    return ""

def extract_skills(text):
    skills_text = extract_section(text, r'SKILLS|TECHNICAL SKILLS', r'EXPERIENCE|WORK EXPERIENCE')
    skills = skills_text.splitlines()
    skills = [skill.strip() for skill in skills if skill.strip()]
    return skills

def extract_experience(text):
    experience_text = extract_section(text, r'EXPERIENCE|WORK EXPERIENCE', r'EDUCATION|SKILLS|PROJECTS|POSITION OF RESPONSIBILITY')
    experience = experience_text.splitlines()
    experience = [exp.strip() for exp in experience if exp.strip()]
    return experience

def structure_resume_data(binary_data, file_type='pdf'):
    text = extract_text(binary_data, file_type)
    name = extract_name_combined(text)
    skills = extract_skills(text)
    experience = extract_experience(text)
    
    resume_data = {
        "name": name,
        "skills": skills,
        "experience": experience
    }
    
    return resume_data

def process_received_resume(binary_data):
    resume_data = structure_resume_data(binary_data)
    print(json.dumps(resume_data, indent=4))

#example
with open('resume1.pdf', 'rb') as file: 
    binary_data = file.read()

process_received_resume(binary_data)





