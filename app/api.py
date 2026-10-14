"""Run: uvicorn app.api:app --reload  (from the project root, after training)"""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from typing import Literal
from pydantic import BaseModel, Field
from pipeline import PhishGuard

app = FastAPI(title="PhishGuard")
_pg = None

class Check(BaseModel):
    text: str

class Feedback(BaseModel):
    text: str = Field(max_length=5000)
    predicted: Literal["safe", "suspicious", "phishing"]
    correct: Literal["safe", "suspicious", "phishing"]

def _cell(v):
    """Stop spreadsheet apps from running a cell as a formula (CSV injection)."""
    return "'" + v if v[:1] in ("=", "+", "-", "@", "\t", "\r") else v

def pg():
    global _pg
    _pg = _pg or PhishGuard()
    return _pg

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/check")
def check(body: Check):
    if not body.text.strip() or len(body.text) > 5000:
        raise HTTPException(400, "Text must be 1 to 5000 characters")
    return pg().check(body.text)

@app.post("/feedback")
def feedback(body: Feedback):
    f = ROOT / "data/feedback.csv"
    new = not f.exists()
    with open(f, "a", newline="") as fh:
        w = csv.writer(fh)
        if new: w.writerow(["text", "predicted", "correct"])
        w.writerow([_cell(body.text), body.predicted, body.correct])
    return {"saved": True}

@app.get("/")
def index():
    return FileResponse(ROOT / "app/static/index.html")
