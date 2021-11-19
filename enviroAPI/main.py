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
    dtstamps: List[datetime]
    values: List[float]

class TQuality(BaseModel):
    dtstamps: List[datetime] = []
    values: List[float] = []
    quality: List[int] = []


app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount('/static',StaticFiles(directory='static'),name='static')

@app.get('/')
def index(request: Request):

    defaultdata = '''
2021-03-07 00:50,3.9
2021-03-07 01:00,5.1
2021-03-07 01:10,5.9
2021-03-07 01:20,5.1
2021-03-07 01:30,5.1
2021-03-07 01:40,5.1
2021-03-07 01:50,5.1
2021-03-07 02:00,5.7
2021-03-07 02:10,-16.2
2021-03-07 02:20,6.7
2021-03-07 02:30,-5.8
2021-03-07 02:40,6.7
2021-03-07 02:50,26.5'''

    return templates.TemplateResponse(
        'enviroUI.html',
        {
            'request':request,
            'defaultdata':defaultdata
        }
    )

@app.post("/checkdata/2m_air_temperature", response_model=TQuality)
async def loadT(T:Temperatures):
    #Load data into a pandas DF
    dts = pd.DatetimeIndex(T.dtstamps)
    data = pd.DataFrame(
        {
            'values':T.values
        },
        index=dts
    )

    #Check data
    data_flagged = envirodataqc.check_vals(data['values'],'air_temperature')
    
    #Calculate the maximum flag
    data_flagged['max_flag'] = data_flagged[['flags_range','flags_rate','flags_flat']].max(1)

    print(data_flagged.head(20))

    #Convert to output
    response = TQuality()
    response.dtstamps = T.dtstamps
    response.values = T.values
    response.quality = data_flagged['max_flag'].to_list()

    return response