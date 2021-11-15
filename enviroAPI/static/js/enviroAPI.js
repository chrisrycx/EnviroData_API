//Test plotly

//Event handler
var inputform = document.getElementById('datainput')
inputform.onsubmit = test

TESTER = document.getElementById('tester');

var dts = [
    '2021-03-07 00:50',
    '2021-03-07 01:00',
    '2021-03-07 01:10',
    '2021-03-07 01:20',
    '2021-03-07 01:30',
    '2021-03-07 01:40',
    '2021-03-07 01:50',
    '2021-03-07 02:00',
    '2021-03-07 02:10',
    '2021-03-07 02:20',
    '2021-03-07 02:30',
    '2021-03-07 02:40',
    '2021-03-07 02:50'
]

var y = [3.9,5.1,5.9,5.1,5.1,5.1,5.1,5.7,-16.2,6.7,5.8,-6.7,26.5]

var quality = [0,0,0,1,1,1,1,0,2,0,0,1,2]

Plotly.newPlot( TESTER, [{
    x: dts,
    y: y }], {
    margin: { t: 0 } } 
);

//Functions
function test(event){
    event.preventDefault()
    console.log("in test function")

    //Create line for all data
    let dataline = {
        x: dts,
        y: y,
        mode: 'lines',
        showlegend: false
    }

    //Extract suspicious and bad data points
    dts_susp = []
    dts_bad = []
    y_susp = []
    y_bad = []
    for(let i = 0; i < quality.length; i++){
        if(quality[i] == 1){
            dts_susp.push(dts[i])
            y_susp.push(y[i])
        }else if(quality[i] == 2){
            dts_bad.push(dts[i])
            y_bad.push(y[i])
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
            size: '5'
        }
    }

    let points_bad = {
        x: dts_bad,
        y: y_bad,
        mode: 'markers',
        name: 'Bad',
        marker: {
            color: 'red',
            size: '5'
        }
    }


    Plotly.newPlot(TESTER,[dataline,points_susp,points_bad]);
    
}


