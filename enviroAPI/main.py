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
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import Button, TextAreaInput, CustomJS, CDSView, BooleanFilter
from bokeh.embed import components
from bokeh.transform import factor_mark
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
    return templates.TemplateResponse(
        'enviroUI.html',
        {
            'request':request
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