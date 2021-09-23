'''
EnviroData QC API Demo
'''
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import envirodataqc
import pandas as pd


class Temperature(BaseModel):
    auth_token: str
    dataids: List[int]
    dtstamps: List[datetime]
    values: List[float]

app = FastAPI()

@app.post("/checkdata/2m_air_temperature")
async def loadT(T:Temperature):
    #Load data into a pandas DF
    dts = pd.DatetimeIndex(T.dtstamps)
    data = pd.DataFrame(
        {
            'data_id':T.dataids,
            'values':T.values
        },
        index=dts
    )

    #Check data
    data_flagged = envirodataqc.check_vals(data['values'],'air_temperature')
    print(data_flagged.head())

    #Convert to dictionary
    data_flagged_json = data_flagged.to_json()

    return data_flagged_json