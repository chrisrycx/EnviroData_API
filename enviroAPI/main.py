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
from bokeh.models import Button, CustomJS
from bokeh.embed import components
import envirodataqc
import pandas as pd


class Temperatures(BaseModel):
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
    #Build Bokeh ColumnDataSource from default data
    data = {'dt':[],'T':[]}
    for row in testdata:
        rowdt = datetime.strptime(row[0],'%Y-%m-%d %H:%M')
        data['dt'].append(rowdt)
        data['T'].append(row[1])
    dsource = ColumnDataSource(data=data)

    #Create a button
    button = Button(label='Check Data')
    button.js_on_click(CustomJS(code="""
        //Test a API request
        let testdata = {
            dtstamps: ['2021-01-10 10:00','2021-01-10 10:15'],
            values: [10.5,11.2]
        }
        fetch('/checkdata/2m_air_temperature',{
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(testdata)
        })
        .then(response => response.json())
        .then(data => console.log(data))
    
    """
    "console.log('button: click!', this.toString())"))

    #Generate initial Bokeh plot
    Tplot = figure(
            plot_width=500,
            plot_height=350,
            toolbar_location=None)
    Tplot.line(source=dsource,x='dt',y='T')

    script, divs = components([Tplot,button])

    return templates.TemplateResponse(
        'enviroUI.html',
        {
            'request':request,
            'data':testdata,
            'bokehscript':script,
            'chart':divs[0],
            'button':divs[1]
        }
    )


@app.post("/checkdata/2m_air_temperature")
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
    print(data_flagged.head())

    #Convert to dictionary
    data_flagged_json = data_flagged.to_json()

    return data_flagged_json