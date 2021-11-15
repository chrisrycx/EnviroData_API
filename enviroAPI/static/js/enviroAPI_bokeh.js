//Javascript for interacting with API

//Event handler
var inputform = document.getElementById('datainput')
inputform.onsubmit = test

//Functions
function test(event){
    event.preventDefault()
    //console.log(this[0].value)
    let data = new FormData(this)
    for(const v of data){
        console.log(v)
    }
}

//Try a bokeh plot
const plt = Bokeh.Plotting
const x = Bokeh.LinAlg.linspace(-0.5, 20.5, 10);
const y = x.map(function (v) { return v * 0.5 + 3.0; });
const source = new Bokeh.ColumnDataSource({ data: { x: x, y: y } });

const Tplot = plt.figure({
    plot_width: 500,
    plot_height: 350
})

const myline = Tplot.line({
    source: source,
    x: 'x',
    y: 'y'
})

plt.show(Tplot)


/*
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
    */
