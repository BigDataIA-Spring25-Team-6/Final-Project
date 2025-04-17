# backend/api/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.crew_config import run_faq_pipeline

app = FastAPI()

class FAQRequest(BaseModel):
    query: str
    role: str
    company: str

@app.post("/faq")
def get_faq_answer(req: FAQRequest):
    try:
        result = run_faq_pipeline(
            faq_query=req.query,
            job_role=req.role,
            company=req.company
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Request failed."))
        
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
