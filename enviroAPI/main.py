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

testdata = [
    ("2021-03-07 00:50",3.9,0),
    ("2021-03-07 01:00",5.1,0),
    ("2021-03-07 01:10",5.9,0),
    ("2021-03-07 01:20",5.1,0),
    ("2021-03-07 01:30",5.1,2),
    ("2021-03-07 01:40",5.1,0),
    ("2021-03-07 01:50",5.1,0),
    ("2021-03-07 02:00",5.7,0),
    ("2021-03-07 02:10",-16.2,1),
    ("2021-03-07 02:20",6.7,0),
    ("2021-03-07 02:30",-5.8,0),
    ("2021-03-07 02:40",6.7,2),
    ("2021-03-07 02:50",26.3,0)
]

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount('/static',StaticFiles(directory='static'),name='static')

@app.get('/')
def index(request: Request):
    #Build Bokeh ColumnDataSource from default data
    #Also convert default data to string for loading
    #to textarea
    data = {'dt':[],'T':[],'quality':[]}
    datastr = ''
    for row in testdata:
        rowdt = datetime.strptime(row[0],'%Y-%m-%d %H:%M')
        data['dt'].append(rowdt)
        data['T'].append(row[1])
        data['quality'].append(row[2])

        rowstr = ','.join([row[0],str(row[1])]) + '\n'
        datastr = datastr + rowstr

    #Delete last \n character
    datastr = datastr[:-1]

    dsource = ColumnDataSource(data=data)
    filter_mod = [True if y_val == 1 else False for y_val in dsource.data['quality']]
    filter_bad = [True if y_val == 2 else False for y_val in dsource.data['quality']]
    mod_view = CDSView(source=dsource, filters=[BooleanFilter(filter_mod)])
    bad_view = CDSView(source=dsource, filters=[BooleanFilter(filter_bad)])

    #Create the text area
    textarea = TextAreaInput(value=datastr, rows=10)

    #Load data callback
    loaddataJS = CustomJS(args={'textarea':textarea,'chartdata':dsource},code="""
    //Test parsing data from input
    let txtinput = textarea.value;

    //Split by row
    let rows = txtinput.split(/\\r?\\n/);

    //Extract data by row
    let dts = []
    let vals = []
    for(let row of rows){
        let data = row.split(',')
        dts.push(data[0])
        vals.push(data[1])
    }
    let dataset = {
        dtstamps: dts,
        values: vals
    }

    fetch('/checkdata/2m_air_temperature',{
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(dataset)
        })
        .then(response => response.json())
        .then(data => {
            //JS to update chart
            console.log('In final function')
            console.log(data)
            console.log(chartdata)
            chartdata.data['T'] = [5,5,5,5,5,5,5,5,5,5,5,5,5]
            chartdata.data['quality'] = [2,1,2,1,2,1,2,1,2,1,2,1,2]
            chartdata.change.emit()
        })

    """)


    #Create a button and link to a callback
    button = Button(label='Check Data')
    button.js_on_click(loaddataJS)

    #Generate initial Bokeh plot
    Tplot = figure(
            plot_width=500,
            plot_height=350,
            x_axis_type='datetime',
            toolbar_location=None)

    #Add a line for the data
    Tplot.line(source=dsource,x='dt',y='T')

    #Add circles to mark suspicious data points
    Tplot.circle(
        source=dsource,
        view=mod_view,
        x='dt',
        y='T',
        color='yellow',
        size=8,
        legend_label='Suspicious'
        )

    #Add x to mark bad data points
    Tplot.circle_x(
        source=dsource,
        view=bad_view,
        x='dt',
        y='T',
        color='red',
        line_color='black',
        size=8,
        legend_label='Bad'
        )

    script, divs = components([Tplot,textarea,button])

    return templates.TemplateResponse(
        'enviroUI.html',
        {
            'request':request,
            'bokehscript':script,
            'chart':divs[0],
            'textarea':divs[1],
            'button':divs[2]
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