from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import subprocess
import os
import re
import shlex

app = FastAPI()
templates = Jinja2Templates(directory="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {
        "request": request,
        "vulner_status": "",
        "secure_status": ""
    })


@app.post("/vulner-login", response_class=HTMLResponse)
async def vulnerable_upload(request: Request, file: UploadFile = File(...)):
    status = ""
    try:
        # Vuln command
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)


        cmd = f"file {file_path}"
        result = subprocess.run(
            cmd,
            shell=True, #!!!!!!!
            capture_output=True,
            text=True
        )
        status = "success : " + result.stdout

    except Exception as e:
        status = f"Error: {str(e)}"

    return templates.TemplateResponse("main.html", {
        "request": request,
        "vulner_status": status,
        "secure_status": ""
    })


@app.post("/secure-login", response_class=HTMLResponse)
async def secure_upload(request: Request, file: UploadFile = File(...)):
    status = ""
    try:
        # Validation
        if not re.match(r"^[\w\-\.]+$", file.filename):
            raise ValueError("Invalid filename")

        safe_path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
        content = await file.read()

        with open(safe_path, "wb") as f:
            f.write(content)

        # Security command
        result = subprocess.run(
            ["file", shlex.quote(safe_path)], # ekran path
            capture_output=True,
            text=True,
            shell=False # !!!!!!!!!!
        )
        status = "Success"

    except Exception as e:
        status = f"Error: {str(e)}"

    return templates.TemplateResponse("main.html", {
        "request": request,
        "vulner_status": "",
        "secure_status": status
    })