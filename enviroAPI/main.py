'''
EnviroData QC API Demo
'''
from typing import Optional, List

from fastapi import FastAPI
from pydantic import BaseModel


class Temperature(BaseModel):
    dataids: List[int]
    dtstamps: List[str]
    values: List[float]

app = FastAPI()

@app.post("/checkdata/2m_air_temperature")
async def loadT(T:Temperature):
    mid = T.dataids
    dt = T.dtstamps
    val = T.values 

    return {
        "message": "working",
        "Temperature":dt,
        "Value":val
        }