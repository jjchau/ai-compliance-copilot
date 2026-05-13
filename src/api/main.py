from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.api.data_loader import cases, case_lookup

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Compliance Copilot API is running!"}

@app.get("/cases")
def get_cases():
    #return {"cases": cases}
    return cases

@app.get("/cases/{trade_id}")
def get_case(trade_id: str):
    case = case_lookup.get(trade_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case