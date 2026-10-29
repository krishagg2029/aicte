"""Document reader: image/PDF -> {type, fields}. Two engines:
 1. Claude vision (if ANTHROPIC_API_KEY set) - best accuracy, understands layout.
 2. Tesseract OCR + keyword classifier + regex (offline baseline, no API needed)."""
import re, io, os, json, base64
from PIL import Image, ImageOps
import pytesseract, fitz

KEYS = {  # distinctive phrases per document type (classifier)
 "society": ["certificate of registration", "registrar of societies"],
 "pan": ["income tax", "permanent account"],
 "land": ["land document", "sale deed", "ownership"],
 "noc": ["no objection", "affiliation"],
 "fire": ["fire safety", "fire department"]}

def to_images(data: bytes, filename: str):
    if filename.lower().endswith(".pdf"):
        doc = fitz.open(stream=data, filetype="pdf")
        return [Image.open(io.BytesIO(p.get_pixmap(dpi=200).tobytes("png"))) for p in list(doc)[:2]]
    return [Image.open(io.BytesIO(data))]

def ocr_text(imgs):
    out = []
    for im in imgs:
        g = ImageOps.autocontrast(ImageOps.grayscale(im))
        out.append(pytesseract.image_to_string(g, config="--psm 6"))
    return "\n".join(out)

def parse(text: str):
    low = text.lower()
    score = {k: sum(low.count(w) for w in ws) for k, ws in KEYS.items()}
    best = max(score, key=score.get)
    typ = best if score[best] > 0 else "other"
    g = lambda r: (re.search(r, text, re.I | re.M) or [None, None])[1]
    pan = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)
    return {"type": typ, "confidence": round(min(1, .5 + .25 * score[best]), 2) if typ != "other" else 0.2,
            "readable": len(text.strip()) > 15,
            "name": (g(r"(?:society|institute|premises|owner|name)\s*:\s*(.+)") or "").strip() or None,
            "pan": pan.group(0) if pan else None, "regno": g(r"reg\s*no\s*:\s*(\S+)"),
            "validTill": g(r"valid\s*till\s*:\s*(\d{4}-\d{2}-\d{2})"), "area": g(r"area\s*:\s*([\d.]+)"),
            "summary": f"Detected as {typ} by OCR keyword classifier", "flags": []}

PROMPT = """You verify AICTE (India) application documents. Reply ONLY with JSON:
{"type":"society|pan|land|noc|fire|other","confidence":0-1,"readable":true|false,"name":str|null,"pan":str|null,
"regno":str|null,"validTill":"YYYY-MM-DD"|null,"area":str|null,"summary":"one line","flags":["only VISIBLE signs of alteration,
mismatched fonts, missing seal/signature/QR, blur on key fields"]}. society=society/trust registration cert, pan=PAN card,
land=land ownership doc, noc=university NOC/affiliation, fire=fire safety cert. Never guess unseen values; use null."""

def claude_read(imgs):
    import anthropic
    c = anthropic.Anthropic()
    content = []
    for im in imgs:
        b = io.BytesIO(); im.convert("RGB").save(b, "JPEG", quality=88)
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                        "data": base64.b64encode(b.getvalue()).decode()}})
    content.append({"type": "text", "text": PROMPT})
    r = c.messages.create(model=os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=800,
                          messages=[{"role": "user", "content": content}])
    t = r.content[0].text
    return json.loads(t[t.find("{"): t.rfind("}") + 1])

def read_document(data: bytes, filename: str, engine: str = "auto"):
    imgs = to_images(data, filename)
    if engine == "claude" or (engine == "auto" and os.getenv("ANTHROPIC_API_KEY")):
        try: return {**claude_read(imgs), "engine": "claude-vision"}
        except Exception as e: print("Claude failed, using OCR:", e)
    return {**parse(ocr_text(imgs)), "engine": "tesseract"}
