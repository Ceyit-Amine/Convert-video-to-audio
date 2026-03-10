# YouTube to MP3 Converter

A sleek, modern web application that allows you to paste a YouTube video link and download its audio as an MP3 file.

## Features
- **FastAPI Backend**: Fast, asynchronous Python backend.
- **yt-dlp**: Reliable YouTube extraction using the best-in-class tool.
- **Premium UI**: Glassmorphism design and smooth animations built with pure CSS and JS.

## Requirements
1. **Python 3.8+**
2. **FFmpeg**: `yt-dlp` requires `ffmpeg` to extract and convert audio to MP3 format. You MUST have `ffmpeg` installed and added to your system's PATH. 
    - Windows: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or install via winget: `winget install ffmpeg`

## Installation & Running

1. Open your terminal in the project directory.
2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\activate
   ```
3. Run the application:
   ```powershell
   uvicorn main:app --reload
   ```
4. Open your browser and navigate to `http://127.0.0.1:8000`.
"# Convert-video-to-audio" 
