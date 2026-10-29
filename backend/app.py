"""FastAPI server: serves the UI and the /api/read document-understanding endpoint."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from reader import read_document
app = FastAPI(title="AICTE PreCheck")

@app.post("/api/read")
async def read(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 15_000_000: raise HTTPException(413, "File too large")
    try: return read_document(data, file.filename or "upload.png")
    except Exception as e: raise HTTPException(422, f"Could not read document: {e}")

@app.get("/api/health")
def health(): return {"ok": True, "engine": "claude-vision" if os.getenv("ANTHROPIC_API_KEY") else "tesseract"}

app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static"), html=True), name="ui")
