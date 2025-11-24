from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import shutil
from rag_manager import RAGManager
import json

app = FastAPI(title="QA Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSET_PATH = "./assets"


rag_agent = None 


def get_rag_agent():
    global rag_agent
    if rag_agent is None:
        print("Initializing RAG Agent (Loading Models)...")
        rag_agent = RAGManager()
        print("RAG Agent ready.")
    return rag_agent

class TestCaseRequest(BaseModel):
    query: str

class ScriptRequest(BaseModel):
    test_case: dict
    html_filename: str

@app.get("/")  
def health_check():
    return {"status": "running"}

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    if not os.path.exists(ASSET_PATH):
        os.makedirs(ASSET_PATH)
        
    saved_files = []
    for file in files:
        file_location = f"{ASSET_PATH}/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        saved_files.append(file.filename)
        
    return {"message": f"Uploaded {len(saved_files)} files", "files": saved_files}

@app.post("/build-kb/")
async def build_knowledge_base():
    try:
        
        agent = get_rag_agent() 
        status = agent.ingest_documents()
        return {"status": "success", "message": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-tests/")
async def generate_tests(request: TestCaseRequest):
    try:
        
        agent = get_rag_agent()
        result = agent.generate_test_cases(request.query)
        try:
            clean_result = result.replace("```json", "").replace("```", "").strip()
            json_data = json.loads(clean_result)
            return {"test_cases": json_data, "raw_text": result}
        except:
            return {"test_cases": [], "raw_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-script/")
async def generate_script(request: ScriptRequest):
    try:
        html_path = f"{ASSET_PATH}/{request.html_filename}"
        if not os.path.exists(html_path):
            raise HTTPException(status_code=404, detail="HTML file not found in assets")
            
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        
        agent = get_rag_agent()
        script = agent.generate_selenium_script(request.test_case, html_content)
        return {"script": script}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
