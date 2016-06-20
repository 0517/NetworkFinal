
$(document).ready(function(){

    client = new Client();

    $(".btn-login").click(function() {
        client.connect();
    });

//    $("#fileButton").click(function() {
//        client.upLoad();
//    });
    $('#fileButton').on('click', function () {
        var $btn = $(this).button('loading');
        client.upLoad();
        // business logic...
//      $btn.button('reset');
    });

//    $("#createButton").click(function() {
//        client.upLoad();
//    });
    $('#createButton').on('click', function () {
        var $btn = $(this).button('loading');
        var name = $('#create').val();
        client.mkd(name);
        // business logic...
//      $btn.button('reset');
    });

    $('.back').on('click', function(e){
        log("back!!");
        e.preventDefault();
        if (client.pwd.length == 1){
            $.scojs_message('No back dictionary', $.scojs_message.TYPE_ERROR);
        } else {
//            client.cdup();
            client.cwd('..');
        }
    })

});

function updateClick() {
    $.each($('.download'), function(){
        $(this).on('click', function(e){
            e.preventDefault();
            var name = $(this).parent().parent().parent().parent().find('.name').text();
            client.downloadData(name);
        });
    });

    $.each($('.file_delete'), function(){
        $(this).on('click', function(e){
            e.preventDefault();
            var name = $(this).parent().parent().parent().parent().find('.name').text();
            client.delete(name);
        });
    });

    $.each($('.dictionary'), function(){
        $(this).on('click', function(e){
            e.preventDefault();
//            log($(this).find('.name').text());
            client.cwd($(this).find('.name').text())
        });
    });

    $.each($('.dir_delete'), function(){
        $(this).on('click', function(e){
            e.preventDefault();
            var name = $(this).parent().parent().parent().parent().find('.name').text();
            client.rmd(name);
        });
    });

}

function log(message) {
    console.log(message);
}

function DataSocket(type) {

    var _this = this;
    this.type = type;
    this.socket = null;
    this.name = "";
    this.connect = function(ip, port) {
        log('connecting');
        var url = "ws://" + ip + ":" + port + "/";
        this.socket =  new WebSocket(url);
        this.socket.onopen = function(event) {
            log(event);
            client.isPasv = false;
            if (_this.type == 'NLST') {
                client.doSend('NLST')
            } else if (_this.type == 'STOR') {
                client.sendFile();
            } else if (_this.type == 'RETR') {
                _this.name = client.currentFile;
                client.doSend('RETR ' + _this.name);
            }
        };
        this.socket.onmessage = function(event) {
            _this.onMessage(event);
        };

    };
    this.onMessage = function(event) {
        log('data');
        log(event);
        if (this.type == 'NLST') {
            client.processNlst(event.data);
        } else if (this.type == 'RETR') {
            var blob = event.data;
            saveAs(blob, this.name);
            this.socket.close();
            client.data_socket[this.type] = undefined;
        }

    };


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
    this.currentFile = "";
    this.isTimeOut = false;
    this.data_socket = {
        'NLST': null,
        'STOR': null,
        'RETR': null
    };
    this.re = /\((\w*.+)/;
    this.file_row = $('#file-tmp').clone();
    this.fold_row = $('#folder-tmp').clone();

    this.connect = function() {

        var ip = $("#ip").val();
        var port = $("#port").val();
        var url = "ws://" + ip + ":" + port + "/";

        try{
            window.setTimeout(this.checkTimeOut, 3000);
            this.control_socket =  new WebSocket(url);
        } catch (e) {

        }


        this.control_socket.onopen = function(event) {

            log(event);

        };
        this.control_socket.onmessage = function(event) {
            _this.onMessage(event);
        };
        this.control_socket.onerror = function(event) {
//            if (!_this.isLogin) {
//                $.scojs_message('Connect Error!', $.scojs_message.TYPE_ERROR);
//            }
        }
    };

    this.checkTimeOut = function() {
        if (!_this.isTimeOut) {
            $.scojs_message('Connect Error! Wrong ip or port!', $.scojs_message.TYPE_ERROR);
        }
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
            this.isTimeOut = true;
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
            this.data_socket[this.currentType].connect(ip, port);


        } else if (event.data.substring(0, 3) == '125') {

        } else if (event.data.substring(0, 3) == '250') {
//            $.scojs_message('Upload successfully!', $.scojs_message.TYPE_OK);
            this.nlst();

        }  else if (event.data.substring(0, 3) == '225') {

            if($('#fileButton').button().text() == "Waiting...") {
                $('#fileButton').button('reset');
                $.scojs_message('Upload successfully!', $.scojs_message.TYPE_OK);
                this.nlst();
                $('.close').click();
                this.data_socket['STOR'].socket.close();
                this.data_socket['STOR'] = undefined;
            } else if($('#createButton').button().text() == "Waiting...") {
                $('#createButton').button('reset');
                $.scojs_message('Create successfully!', $.scojs_message.TYPE_OK);
                this.nlst();
                $('.close').click();
            }
//            else if($('#fileButton').button().text() == "Waiting...") {
//                $('#fileButton').button('reset');
//            }
        } else {
            this.isPasv = false;
            alert(event.data);
        }
    };

    this.doSend = function(message) {

        log(message);
        this.control_socket.send(message + '\r\n');

    };

    this.pasv = function(type){
        // type: NLST, STOR, RETR
//        if (!(type in this.data_socket.altKey)) {
//            alert("Wrong type")
//        } else
        if (!this.isPasv) {

            this.currentType = type;
            this.isPasv = true;
            this.doSend("PASV " + type);

        } else {
//            alert("A data socket is connecting.")
        }

    };

    this.nlst = function() {
        var type = 'NLST';
        if (this.data_socket[type] != undefined) {

        } else {
            this.pasv(type);
        }
    };

    this.processNlst = function (data) {
        this.updateCwd();
        this.isPasv = false;
        this.data_socket['NLST'].socket.close();
        this.data_socket['NLST'] = undefined;
        var obj = JSON.parse(data);
        var table = $('.file-list tbody');
        table.empty();

        for (dir in obj['dir']) {
            var row = this.fold_row.clone();
            row.find('.name').text(obj['dir'][dir]);
            table.append(row);
        }

        for (file in obj['file']) {
            var row = this.file_row.clone();
            row.find('.name').text(obj['file'][file]);
            table.append(row);
        }
        updateClick();
    };

    this.upLoad = function() {

        var type = 'STOR';
        if (this.data_socket[type] != undefined) {

        } else {
            this.pasv('STOR');
        }

    };

    this.sendFile = function() {

        var p = $('#file').val();
        var file_name = p.substring(p.lastIndexOf("\\")+1);
        this.doSend('STOR ' + file_name);
        var resultfile = reader.result;
        this.data_socket['STOR'].socket.binaryType = "arraybuffer";
        this.data_socket['STOR'].socket.send(resultfile, opcode=0x2);

    };

    this.downloadData = function(name) {

        var type = 'RETR';
        this.currentFile = name;
        if (this.data_socket[type] != undefined) {

        } else {
            this.pasv('RETR');
        }

    };

    this.cwd = function(dir) {
        if (dir == '..') {
            this.pwd.splice(this.pwd.length-1, 1);
        } else {
            this.pwd.push(dir);
        }

        this.doSend('CWD ' + dir);
    };

    this.rmd = function(dir) {
        this.doSend('RMD ' + dir);
        $.scojs_message('Successfully Delete!', $.scojs_message.TYPE_OK);
    };

    this.delete = function(dir) {
        this.doSend('DELETE ' + dir);
        $.scojs_message('Successfully Delete!', $.scojs_message.TYPE_OK);
    };

    this.mkd = function(dir) {
        this.doSend('MKD ' + dir);
    };

    this.cdup = function() {
        this.doSend('CDUP');
        this.pwd.splice(this.pwd.length-1, 1);
    };

    this.updateCwd = function() {
        $('.path').empty();
        var item = "";
        for (var i = 0; i < this.pwd.length; i++) {
            item = "";
            if (i != 0) {
                item += ' >> '
            }
            item += this.pwd[i];

            $('.path').append(item);
        }
    }


}

