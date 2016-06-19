
$(document).ready(function(){

    client = new Client();

    $(".btn-login").click(function() {
        client.connect();
    });

});

function log(message) {
    console.log(message);
}

function DataSocket(type) {

    var _this = this;
    this.type = type;
    this.socket = null;
    this.connect = function(ip, port) {
        var url = "ws://" + ip + ":" + port + "/";
        this.socket =  new WebSocket(url);
        this.socket.onopen = function(event) {
            log(event);
        };
        this.socket.onmessage = function(event) {
            _this.onDataMessage(event);
        };
    };
    this.onMessage = function(event) {
        if (this.type == 'NLTS') {
            client.processNlst(event.data);
        }
    }

}



function Client() {

    if (_this != undefined ) {
        return _this;
    }

    this.pwd = ["root"];
    var _this = this;
    this.control_socket = null;
    this.isPasv = false;
    this.currentType = "";
    this.data_socket = {
        'NLST': null,
        'STOR': null,
        'RETR': null
    };
    this.re = /\((\w*.+)/;

    this.connect = function() {

        var ip = $("#ip").val();
        var port = $("#port").val();
        var url = "ws://" + ip + ":" + port + "/";

        this.control_socket =  new WebSocket(url);

        this.control_socket.onopen = function(event) {
            log(event);
        };
        this.control_socket.onmessage = function(event) {
            _this.onMessage(event);
        };
    };

    this.login = function() {

        var user = $("#user").val();
        this.doSend("USER " + user + "\r\n");

    };

    this.onMessage = function(event) {
        console.log(event);

        if (event.data.substring(0, 3) == '331') {

            this.doSend("PASS " + $("#password").val() + "\r\n");

        } else if (event.data.substring(0, 3) == '220') {

            this.login();

        } else if (event.data.substring(0, 3) == '230') {

            log("login success");
            $(".login").fadeOut("fast");
            $(".main_board").fadeIn("fast");
            this.nlst();

        } else if (event.data.substring(0, 3) == '227') {

            host = this.re.exec(event.data)[1].split(')')[0];
            ip = host.split(',')[0];
            port = host.split(',')[1];
            this.data_socket[this.currentType] = new DataSocket(this.currentType);
            this.data_socket[this.currentType].connect(ip,port);
            this.isPasv = false;

        } else {
            this.isPasv = false;
            alert(event.data);
        }
    };

//    this.onDataMessage = function(event) {
//        console.log(event);
//        //writeToScreen("response: " + evt.data + '\n');
//        if (!isNlst) {
//            blob = evt.data;
//            saveAs(blob, "test.jpg");
//        } else {
//            isNlst = false;
//            writeToScreen("response: " + evt.data + '\n')
//        }
//        socket.close();
//    };

    this.doSend = function(message) {

        log(message);
        this.control_socket.send(message);

    };

    this.pasv = function(type){
        // type: NLST, STOR, RETR
//        if (!(type in this.data_socket.altKey)) {
//            alert("Wrong type")
//        } else
        if (!this.isPasv) {

            this.currentType = type;
            this.isPasv = true;
            this.doSend("PASV " + type + "\r\n");

        } else {
            alert("A data socket is connecting.")
        }

    };

    this.nlst = function() {
        var type = 'NLST';
        if (this.data_socket[type] != undefined) {

        } else {
            this.pasv('NLST');
        }
    };

    this.processNlst = function (data) {
        var obj = JSON.parse(data);
        var table = $('tbody');
        var file_row = $('#file-tmp').clone();
        var fold_row = $('#folder-tmp').clone();
        table.empty();

        for (dir in obj['dir']) {
            fold_row.find('.name').text(dir);
            table.append(fold_row);
            fold_row = $('#folder-tmp').clone();
        }

        for (file in obj['file']) {
            file_row.find('.name').text(file);
            table.append(file_row);
            file_row = $('#file-tmp').clone();
        }
    };


}

