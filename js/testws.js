

$(document).ready(function(){
    //if($.cookie("name")=="null"){
    //    location.href="/Wave/login.html";
    //}
    //$("#self").text($.cookie("name"));
    //connect();
});

re = /\((\w*.+)/;


function init() {
    //document.myform.url.value = "ws://localhost:9876/";
    document.myform.url.value = "ws://127.0.0.1:12344/";
    document.myform.inputtext.value = "Hello World!";
    document.myform.disconnectButton.disabled = true;
}

function doConnect() {
    websocket = new WebSocket(document.myform.url.value);
    websocket.onopen = function(evt) { onOpen(evt) };
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };
}

function dataConnect(ip, port) {
    url = "ws://" + ip + ":" + port + "/";
    socket = new WebSocket(url);
    socket.onopen = function(evt) { onOpen(evt) };
    socket.onclose = function(evt) { onClose(evt) };
    socket.onmessage = function(evt) { onMessage(evt) };
    socket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt) {
    writeToScreen("connected\n");
    document.myform.connectButton.disabled = true;
    document.myform.disconnectButton.disabled = false;
}

function onClose(evt) {
    writeToScreen("disconnected\n");
    document.myform.connectButton.disabled = false;
    document.myform.disconnectButton.disabled = true;
}

function onMessage(evt) {
    console.log(evt.data);
    if (evt.data.substring(0, 3) == '227') {
        host = re.exec(evt.data)[1].split(')')[0];
        ip = host.split(',')[0];
        port = host.split(',')[1];
        dataConnect(ip, port);
    }
    writeToScreen("response: " + evt.data + '\n');
}

function onDataMessage(evt) {
    console.log(evt.data);
    //writeToScreen("response: " + evt.data + '\n');
    blob = evt.data;
    saveAs(blob, "test.jpg");
    socket.close();
}

function onError(evt) {
    writeToScreen('error: ' + evt.data + '\n');
    websocket.close();
    document.myform.connectButton.disabled = false;
    document.myform.disconnectButton.disabled = true;
}

function doSend(message) {
    writeToScreen("sent: " + message + '\n');
    websocket.send(message);
}

function writeToScreen(message) {

    document.myform.outputtext.value += message;
    document.myform.outputtext.scrollTop = document.myform.outputtext.scrollHeight;
}

window.addEventListener("load", init, false);

function sendText() {
    doSend( document.myform.inputtext.value );
}

function sendFile() {
    websocket.send('STOR testsend.jpg');
    resultfile = reader.result;
    res = new Blob([resultfile]);
    console.log(res);
    socket.send(res);
}

function clearText() {
    document.myform.outputtext.value = "";
}

function doDisconnect() {
    websocket.close();
}

function login(user, passw) {
    doSend("USER " + user + "\r\n");
    doSend("PASS " + user + "\r\n");
}

function pasv() {
    doSend('PASV\r\n');
}

function nlst() {
    doSend('NLST\r\n');
}

