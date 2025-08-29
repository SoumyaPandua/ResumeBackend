import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from api import main as run_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-frontend-git-main-axyz10649ram-gmailcoms-projects.vercel.app"],  # you can also allow "*" for Render testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run-pipeline")
async def trigger_pipeline_from_uploads(
    jd: UploadFile = File(...),
    resumes: list[UploadFile] = File(...),
):
    try:
        temp_dir = tempfile.mkdtemp()
        resume_folder = os.path.join(temp_dir, "resumes")
        jd_folder = os.path.join(temp_dir, "jd")

        os.makedirs(resume_folder, exist_ok=True)
        os.makedirs(jd_folder, exist_ok=True)

        jd_path = os.path.join(jd_folder, jd.filename)
        with open(jd_path, "wb") as f:
            f.write(await jd.read())

        for resume in resumes:
            resume_path = os.path.join(resume_folder, resume.filename)
            with open(resume_path, "wb") as f:
                f.write(await resume.read())

        results = run_pipeline(resume_folder, jd_folder)
        return JSONResponse(content={"status": "success", "results": results}, status_code=200)

    except Exception as e:
        print("[ERROR] Pipeline failed:", e)
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


# 👇 Add this block so Render knows how to start
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render sets $PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)