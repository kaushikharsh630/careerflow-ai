from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import functions
import os
import shutil

app = FastAPI()

# 1. ANALYZE ENDPOINT
@app.post("/analyze-match")
async def analyze_match(
    resume_file: UploadFile = File(...), 
    job_description: str = Form(...)
):
    # Extract text once
    raw_text = functions.extract_text(resume_file.file, resume_file.filename)
    
    # Perform Analysis
    analysis = functions.analyze_job_match(raw_text, job_description)
    
    # Return both analysis AND extracted text (so frontend doesn't need to re-upload)
    return {
        "analysis": analysis,
        "extracted_resume_text": raw_text
    }

# 2. GENERATE ENDPOINT (Now accepts extracted text directly)
@app.post("/generate-kit")
async def generate_kit(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    tone: str = Form(...),
    q_count: int = Form(...),
    generate_audio: bool = Form(...)
):
    # 1. Resume
    latex_code = functions.generate_latex_resume(resume_text, job_description, tone)
    
    # 2. Cover Letter
    cl_text = functions.generate_cover_letter_text(resume_text, job_description, tone)
    
    # 3. Interview Q&A
    qa_text = functions.generate_interview_qa(job_description, q_count)
    
    # 4. Audio (Optional)
    audio_path = None
    if generate_audio:
        audio_path = functions.generate_audio_from_text(qa_text, "interview.mp3")

    return {
        "latex_resume": latex_code,
        "cover_letter_text": cl_text,
        "interview_qa": qa_text,
        "audio_path": audio_path # Frontend will need to download this via a separate GET if needed, or we send bytes
    }

# 3. HELPER TO SERVE AUDIO FILE
@app.get("/get-audio")
def get_audio(filename: str):
    path = f"/tmp/{filename}" if os.name == 'posix' else filename
    if os.path.exists(path):
        return FileResponse(path, media_type="audio/mpeg", filename="interview.mp3")
    return {"error": "File not found"}