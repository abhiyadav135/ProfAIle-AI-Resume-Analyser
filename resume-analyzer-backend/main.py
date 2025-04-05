from ai_engine import analyze_resume

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Resume Analyzer Backend is running."}

@app.post       ("/analyze")
async def analyze(resume: UploadFile = File(...), jd: UploadFile = File(...)):
    resume_content = await resume.read()
    jd_content = await jd.read()

    # Just a mock response for now
    return {
        "match_score": 72.5,
        "skill_gaps": ["Python", "Docker"],
        "suggestions": [
            "Include more job-specific keywords like Python.",
            "Consider adding Docker experience."
        ],
        "status": "Success"
    }
