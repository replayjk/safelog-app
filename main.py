import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from dotenv import load_dotenv
from pdf_generator import generate_pdf
from db import init_db

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/cases", StaticFiles(directory="cases"), name="cases")
app.mount("/pdf_reports", StaticFiles(directory="pdf_reports"), name="pdf_reports")

init_db()

@app.post("/submit", response_class=RedirectResponse)
async def submit_case(description: str = Form(...), image: UploadFile = File(None)):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    image_path = ""

    # 이미지 저장
    if image is not None and image.filename != "":
        upload_dir = "cases/"
        os.makedirs(upload_dir, exist_ok=True)
        file_extension = image.filename.split(".")[-1]
        file_name = f"{timestamp}.{file_extension}"
        file_path = os.path.join(upload_dir, file_name)

        try:
            with open(file_path, "wb") as f:
                f.write(await image.read())
            image_path = f"/cases/{file_name}"
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")

    # PDF 생성
    pdf_path = generate_pdf(description, image_path, timestamp)

    # 데이터베이스 저장
    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cases (description, image_path, timestamp, pdf_path) VALUES (?, ?, ?, ?)", 
                   (description, image_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pdf_path))
    conn.commit()
    conn.close()

    return RedirectResponse(url=pdf_path, status_code=303)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/report")


@app.get("/report", response_class=HTMLResponse)
async def report_form(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})
