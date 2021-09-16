# main.py

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

class temperature(BaseModel):
    name: str
    description: Optional[str] = None
    value: float

app = FastAPI()

@app.get("/test/{test_id}")
async def loadT(test_id: int, T: temperature):
    return {"message": test_num}
