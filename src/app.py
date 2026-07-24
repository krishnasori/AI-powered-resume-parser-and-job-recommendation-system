from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os
from .database import engine, Base
from .import models

models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Resume Parser SaaS API",
    description="Core backend for parsing resumes and finding job matches."
)

# 1. Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running smoothly!"}

# 2. PDF Upload & Parse Endpoint
@app.post("/api/v1/parse")
async def parse_resume(file: UploadFile = File(...)):
    # Validate that the uploaded file is a PDF
    if file.content_type != "application/pdf" and not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Create a temporary directory to store uploads
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the uploaded file locally so your engine can read it
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # NOTE: Tomorrow we will plug in your skills_engine.py here!
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
        
    finally:
        # Clean up the temporary file after processing
        if os.path.exists(file_path):
            os.remove(file_path)
            
    return {
        "filename": file.filename,
        "status": "success",
        "message": "PDF successfully uploaded and ready for parsing!"
    }