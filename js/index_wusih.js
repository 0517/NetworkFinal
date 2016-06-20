
$(document).ready(function(){

    client = new Client();

    $(".btn-login").click(function() {
        client.connect();
    });

    $(".quit").click(function() {
        client.quit();
    });

    $(".ip").click(function() {
        if (!$(this).hasClass('active')) {
            $('.ftp-list').hide();
            $('.ip-list').show();
            $('.ftp').removeClass('active');
            $(this).addClass('active');
        }
    });

    $(".ftp").click(function() {

        if (!$(this).hasClass('active')) {
            $('.ip-list').hide();
            $('.ftp-list').show();
            $('.ip').removeClass('active');
            $(this).addClass('active');
        }

    });


    $('#fileButton').on('click', function () {
        var $btn = $(this).button('loading');
        client.upLoad();

    });

    $('#createButton').on('click', function () {

        var $btn = $(this).button('loading');
        var name = $('#create').val();
        client.mkd(name);

    });

    $('.back').on('click', function(e){

        log("back!!");
        e.preventDefault();
        if (client.pwd.length == 1){
            $.scojs_message('Already root folder', $.scojs_message.TYPE_ERROR);
        } else {
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

var DataSocketO = {
    _this: this,
    type: "",
    socket: null,
    connect: function() {
        log('connecting');
        var url = "ws://" + ip + ":" + port + "/";
        this.socket =  new WebSocket(url);
        var _this = this;
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
    },
    onMessage : function(event) {

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
    }


};

function DataSocket(type) {
    var ds = Object.create(DataSocketO);
    ds.type = type;
    return ds
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
    this.username = "";
    this.names = [];

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

        }
    };

    this.checkTimeOut = function() {

        if (!_this.isTimeOut) {
            $.scojs_message('Connect Error! Wrong ip or port!', $.scojs_message.TYPE_ERROR);
        }

    };

    this.login = function() {

        var user = $("#user").val();
        this.username = user;
        $('.username').text(user);
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

        } else if (event.data.substring(0, 3) == '221') {

            $.scojs_message('Successfully Quit!', $.scojs_message.TYPE_OK);
            log("quit success");
            this.control_socket.close();
            $(".login").fadeIn("fast");
            $(".main_board").fadeOut("fast");

        } else if (event.data.substring(0, 3) == '250') {

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

        if (!this.isPasv) {

            this.currentType = type;
            this.isPasv = true;
            this.doSend("PASV " + type);

        } else {

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

        this.names = [];
        this.updateCwd();
        this.isPasv = false;
        this.data_socket['NLST'].socket.close();
        this.data_socket['NLST'] = undefined;
        var obj = JSON.parse(data);
        var table = $('.file-list tbody');
        table.empty();

        if (obj['dir'].length == 0 && obj['file'].length == 0) {
            table.append('Nothing');
        }

        for (dir in obj['dir']) {
            var row = this.fold_row.clone();
            row.find('.name').text(obj['dir'][dir]);
            this.names.push(obj['dir'][dir]);
            table.append(row);
        }

        for (file in obj['file']) {
            var row = this.file_row.clone();
            row.find('.name').text(obj['file'][file]);
            this.names.push(obj['file'][file]);
            table.append(row);
        }
        updateClick();

    };

    this.upLoad = function() {

        var type = 'STOR';
        var p = $('#file').val();
        var file_name = p.substring(p.lastIndexOf("\\")+1);
        if (this.checkExsit(file_name)) {
            $.scojs_message('File name exist!', $.scojs_message.TYPE_ERROR);
            $('#fileButton').button('reset');
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
        if (this.checkExsit(dir)) {
            $.scojs_message('File name exist!', $.scojs_message.TYPE_ERROR);
            $('#createButton').button('reset');
        } else {
            this.doSend('MKD ' + dir);
        }
    };


    this.quit = function() {
        this.doSend('QUIT');
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
    };

    this.checkExsit = function(name) {
        for (var i = 0; i < this.names.length; i++) {
            if (this.names[i] == name) return true;
        }
        return false;
    }


}

