import os
import uuid
import asyncio
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import yt_dlp

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Store status of conversions
conversion_status = {}

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert")
async def convert_video(url: str = Form(...)):
    task_id = str(uuid.uuid4())
    conversion_status[task_id] = {"status": "processing", "file_path": None, "error": None}
    
    # Start conversion in background
    asyncio.create_task(run_conversion(task_id, url))
    
    return {"task_id": task_id}

async def run_conversion(task_id: str, url: str):
    try:
        # Generate output path
        output_template = os.path.join(DOWNLOAD_DIR, f"{task_id}_%(title)s.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'ffmpeg_location': r'C:\Users\Amine\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin',
        }
        
        # Run yt-dlp synchronously in a thread
        loop = asyncio.get_event_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                title = info_dict.get('title', 'audio')
                
                # The actual output filename might differ slightly due to sanitization
                # Let's find the file that starts with task_id
                for file in os.listdir(DOWNLOAD_DIR):
                    if file.startswith(task_id) and file.endswith('.mp3'):
                        return os.path.join(DOWNLOAD_DIR, file), title
                return None, None
                
        file_path, title = await loop.run_in_executor(None, download)
        
        if file_path:
            conversion_status[task_id] = {"status": "completed", "file_path": file_path, "title": title}
        else:
            conversion_status[task_id] = {"status": "error", "error": "Download failed: no file found"}
            
    except Exception as e:
        conversion_status[task_id] = {"status": "error", "error": str(e)}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    status = conversion_status.get(task_id)
    if not status:
        return JSONResponse(status_code=404, content={"error": "Sequence not found"})
    return {"status": status["status"], "error": status.get("error"), "title": status.get("title")}

@app.get("/download/{task_id}")
async def download_file(task_id: str):
    status = conversion_status.get(task_id)
    if not status or status["status"] != "completed":
        return JSONResponse(status_code=400, content={"error": "File not ready or not found"})
    
    file_path = status["file_path"]
    filename = status.get("title", "audio") + ".mp3"
    
    return FileResponse(path=file_path, filename=filename, media_type='audio/mpeg')
