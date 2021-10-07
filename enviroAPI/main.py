'''
EnviroData QC API Demo
'''

from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from pydantic import BaseModel
import envirodataqc
import pandas as pd


class Temperatures(BaseModel):
    auth_token: str
    dataids: List[int]
    dtstamps: List[datetime]
    values: List[float]

testdata = [
    ("2021-03-07 00:50",-3.9),
    ("2021-03-07 01:00",-5.1),
    ("2021-03-07 01:10",-5.9),
    ("2021-03-07 01:20",-6.2),
    ("2021-03-07 01:30",-5.1),
    ("2021-03-07 01:40",-5.1),
    ("2021-03-07 01:50",-5.9),
    ("2021-03-07 02:00",-5.7),
    ("2021-03-07 02:10",-6.2),
    ("2021-03-07 02:20",-6,7),
    ("2021-03-07 02:30",-5.8),
    ("2021-03-07 02:40",-6.7),
    ("2021-03-07 02:50",-6.3)
]

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount('/static',StaticFiles(directory='static'),name='static')

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse('enviroUI.html',{'request':request,'data':testdata})


@app.post("/checkdata/2m_air_temperature")
async def loadT(T:Temperatures):
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