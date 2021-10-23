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

testdata = [
    ("2021-03-07 00:50",3.9,0),
    ("2021-03-07 01:00",5.1,0),
    ("2021-03-07 01:10",5.9,0),
    ("2021-03-07 01:20",6.2,0),
    ("2021-03-07 01:30",5.1,1),
    ("2021-03-07 01:40",5.1,1),
    ("2021-03-07 01:50",5.9,0),
    ("2021-03-07 02:00",-5.7,2),
    ("2021-03-07 02:10",6.2,0),
    ("2021-03-07 02:20",6.7,0),
    ("2021-03-07 02:30",-5.8,2),
    ("2021-03-07 02:40",6.7,0),
    ("2021-03-07 02:50",-6.3,2)
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

    dsource = ColumnDataSource(data=data)
    filter_mod = [True if y_val == 1 else False for y_val in dsource.data['quality']]
    filter_bad = [True if y_val == 2 else False for y_val in dsource.data['quality']]
    mod_view = CDSView(source=dsource, filters=[BooleanFilter(filter_mod)])
    bad_view = CDSView(source=dsource, filters=[BooleanFilter(filter_bad)])

    #Create the text area
    textarea = TextAreaInput(value=datastr, rows=10)

    #Test callback
    testJS = CustomJS(args={'chartdata':dsource},code="""
    //JS to update chart
    const data = chartdata.data
    console.log(data)
    data['T'] = data['T'].map(x => x*x)
    chartdata.change.emit()
    """
    )

    testJS2 = CustomJS(code="""
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
    
    """)

    testJS3 = CustomJS(args={'textarea':textarea},code="""
    //Test parsing data from input
    console.log(textarea.value)

    """)

    

    #Create a button
    button = Button(label='Check Data')
    button.js_on_click(testJS3)

    #Generate initial Bokeh plot
    Tplot = figure(
            plot_width=500,
            plot_height=350,
            x_axis_type='datetime',
            toolbar_location=None)

    #Add a line for the data
    Tplot.line(source=dsource,x='dt',y='T')

    #Add scatter plot for quality markers
    '''
    Tplot.scatter(
        source=dsource,
        x='dt',
        y='T',
        marker=factor_mark('quality',markers=['circle'])
    )
    '''
    Tplot.circle(
        source=dsource,
        view=mod_view,
        x='dt',
        y='T',
        color='yellow',
        size=8,
        legend_label='Suspicious'
        )
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