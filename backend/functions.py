import os
import PyPDF2
from docx import Document
from dotenv import load_dotenv
from fpdf import FPDF
from gtts import gTTS
import json
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Setup AI
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    google_api_key="AIzaSyCkDR7EiTh2i94EQdMQk06U3CizKmOawdg" 
    # Make sure your key is in .env or hardcoded here if .env fails
)

def extract_text(file, filename):
    """Reads PDF or DOCX file object."""
    text = ""
    try:
        if filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        elif filename.endswith(".docx"):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return str(e)
    return text

# --- NEW: ANALYSIS FUNCTION ---
def analyze_job_match(resume_text, jd):
    """Returns a JSON analysis of the fit."""
    template = """
    Act as a Hiring Manager. Analyze the fit between this Resume and Job Description.
    
    Resume: {resume}
    Job Description: {jd}
    
    Output a strictly valid JSON object with these keys:
    - "match_score": (integer 0-100)
    - "reasoning": (string, 2 sentences explaining why the score is high or low)
    - "pros": (list of strings, matching skills)
    - "cons": (list of strings, missing critical skills)
    
    Do not output markdown ticks. Just the JSON string.
    """
    prompt = PromptTemplate(input_variables=["jd", "resume"], template=template)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"jd": jd[:1500], "resume": resume_text[:3000]})
    # Clean output to ensure JSON parsing works
    clean_json = response.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_json)
    except:
        # Fallback if AI output is messy
        return {
            "match_score": 50, 
            "reasoning": "Could not parse detailed analysis.", 
            "pros": [], 
            "cons": []
        }

# --- UPDATED: RESUME WITH TONE ---
def generate_latex_resume(resume_text, jd, tone="professional"):
    """Generates LaTeX code tailored to the JD with specific tone."""
    template = """
    Act as a Resume Expert. Rewrite this resume into professional LaTeX code.
    Tone: {tone}.
    
    You MUST inject these keywords from the Job Description: {jd}
    Resume Content: {resume}
    
    Rules:
    1. Output ONLY valid LaTeX code. Start with \\documentclass.
    2. Use the 'article' class or a standard resume template.
    3. Do NOT include markdown ticks.
    """
    prompt = PromptTemplate(input_variables=["jd", "resume", "tone"], template=template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"jd": jd[:1000], "resume": resume_text[:3000], "tone": tone}).replace("```latex", "").replace("```", "")

def generate_cover_letter_text(resume_text, jd, tone="professional"):
    template = """
    Write a {tone} cover letter for this Job Description: {jd}
    Based on this candidate's resume: {resume}
    Keep it under 300 words.
    """
    prompt = PromptTemplate(input_variables=["jd", "resume", "tone"], template=template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"jd": jd[:1000], "resume": resume_text[:3000], "tone": tone})

# --- UPDATED: INTERVIEW Q&A + AUDIO ---
def generate_interview_qa(jd, count=3):
    """Generates Questions AND Answers."""
    template = """
    Generate {count} tough technical interview questions AND sample answers based on this JD: {jd}
    Format as a clean text list:
    Q1: ...
    A1: ...
    """
    prompt = PromptTemplate(input_variables=["jd", "count"], template=template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"jd": jd[:1000], "count": count})

def generate_audio_from_text(text, filename="interview_prep.mp3"):
    """Converts text to MP3 using Google TTS."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        # Save to a generic path that FastAPI can read
        save_path = f"/tmp/{filename}" if os.name == 'posix' else filename
        tts.save(save_path)
        return save_path
    except Exception as e:
        print(f"Audio Error: {e}")
        return None

def create_pdf_from_text(text, filename="output.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    file_path = f"/tmp/{filename}" if os.name == 'posix' else filename
    pdf.output(file_path)
    return file_path