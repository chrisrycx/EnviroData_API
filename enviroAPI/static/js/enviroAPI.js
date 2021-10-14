//Javascript for interacting with API

//Event handler
const inputbtn = document.querySelector('#inputbtn')
inputbtn.addEventListener('click',test)

//Functions
function test(){
    //Turn background of response red
    const responseArea = document.querySelector('#response')
    responseArea.style.backgroundColor = 'red'
}