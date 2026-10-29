# NiyamAI - AI application validator (SIH PS 26261)

Two ways to run it:

## A) Standalone (no install)
Double-click NiyamAI_standalone.html (internet needed for the in-browser OCR, Tesseract.js).
Single file: all HTML, CSS and JavaScript (UI, rule engine, OCR, officer console) are inside it.

## B) Full project with Python backend (reads PDFs + images, optional Claude vision)
    pip install -r requirements.txt         # plus Tesseract: Windows installer / brew install tesseract / apt install tesseract-ocr
    export ANTHROPIC_API_KEY=...            # optional; without it Tesseract is used
    uvicorn backend.app:app --reload        # open http://localhost:8000

## Accuracy report
    python backend/gen_data.py 40           # 200 synthetic documents with ground truth
    python backend/evaluate.py auto

## Files
- NiyamAI_standalone.html   whole app in one file
- static/index.html         same UI, wired to the backend (/api/read)
- backend/reader.py         PDF->image, OCR, document classifier, field extraction, optional Claude vision
- backend/app.py            FastAPI server
- backend/gen_data.py, evaluate.py   synthetic data + accuracy measurement
In the HTML: validate() = every mistake rule; readDoc()/ocrRead() = document understanding; submitApp() = send to storage.
