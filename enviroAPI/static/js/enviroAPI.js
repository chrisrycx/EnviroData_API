//JS for API Demo page

//DOM elements
const chart = document.getElementById('chart');
const responsetxt = document.getElementById('responsetxt')
const inputform = document.getElementById('datainput')
const inputvals = document.getElementById('inputvals')
inputform.onsubmit = sendData

//Initial plot using default data in input
let initialtxt = inputvals.value
let initialdata = parseInput(initialtxt)
initialdata['quality'] = [0,0,0,0,0,0,0,0,0,0,0,0,0]
updateChart(initialdata)

//Functions
function parseInput(inputtxt){
    //Parse CSV data from input to an object

    //Split by row
    let rows = inputtxt.split(/\r?\n/)

    //Truncate rows to limit amount of data that can be set
    let maxrows = 200
    let numrows = rows.length
    if(numrows > maxrows){
        rows = rows.slice(0,maxrows)
    }

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

    return dataset
}

function sendData(event){
    //Send input data to backend
    event.preventDefault()
    let dataset = parseInput(this[0].value)
    
    //Post request
    fetch('/checkdata/2m_air_temperature',{
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(dataset)
    })
    .then(response => response.json())
    .then(data => {
            //Load response to response div
            responsetxt.textContent = JSON.stringify(data, undefined, 2)

            //JS to update chart
            updateChart(data)
        })
}

function updateChart(data){

    //Create the basic layout
    let layout = {
        height: 550,
        yaxis: {
            title: "Temperature"
        },
        legend: {
            x: 0,
            y: 1,
            xanchor: 'left'
        },
        margin: {
            t: 10
        }
    }
    
    //Create line for all data
    let dataline = {
        x: data.dtstamps,
        y: data.values,
        mode: 'lines',
        showlegend: false
    }

    //Extract suspicious and bad data points
    dts_susp = []
    dts_bad = []
    y_susp = []
    y_bad = []
    for(let i = 0; i < data.quality.length; i++){
        if(data.quality[i] == 1){
            dts_susp.push(data.dtstamps[i])
            y_susp.push(data.values[i])
        }else if(data.quality[i] == 2){
            dts_bad.push(data.dtstamps[i])
            y_bad.push(data.values[i])
        }
    }

    //Create markers for susp/bad
    let points_susp = {
        x: dts_susp,
        y: y_susp,
        mode: 'markers',
        name: 'Suspicious',
        marker: {
            color: 'yellow',
            size: '8'
        }
    }

    let points_bad = {
        x: dts_bad,
        y: y_bad,
        mode: 'markers',
        name: 'Bad',
        marker: {
            color: 'red',
            size: '8'
        }
    }

    Plotly.newPlot(chart,[dataline,points_susp,points_bad],layout);
}


