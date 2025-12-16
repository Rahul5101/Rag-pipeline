from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
app = FastAPI()
# Base URL for opening PDF
BASE_URL = "http://localhost:8000/open-pdf?file_path="
# --- STATIC META DATA ---
STATIC_META_DATA = [
    {
        "page": 1,
        "source": r"C:\valiance\navy\worksheet.pdf#page=1"
    },
    {
        "page": 2,
        "source": r"C:\valiance\navy\worksheet.pdf#page=2"
    }
]
# --- FUNCTION TO CONVERT PATHS ---
def convert_meta_data(meta_data):
    updated_meta = []
    for item in meta_data:
        file_path = item["source"]
        # Replace Windows "\" → "/" (important for URLs)
        safe_path = file_path.replace("\\", "/")
        pdf_url = f"{BASE_URL}{safe_path}"
        updated_meta.append({
            "page": item["page"],
            "source": pdf_url
        })
    return updated_meta
# --- API TO RETURN META DATA ---
@app.get("/convert-meta")
def convert_meta_api():
    result = convert_meta_data(STATIC_META_DATA)
    return {"meta_data": result}

{
    "meta_data": [
        {
            "page": 1,
            "source": "http://localhost:8000/open-pdf?file_path=C:/valiance/navy/worksheet.pdf#page=1"
        },
        {
            "page": 2,
            "source": "http://localhost:8000/open-pdf?file_path=C:/valiance/navy/worksheet.pdf#page=2"
        }
    ]
}