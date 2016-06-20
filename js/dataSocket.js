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
            }  else if (_this.type == 'IP') {

                client.doSend('IP');

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

        } else if (this.type == 'IP') {

            client.processIp(event.data);

        }
    }


};

function DataSocket(type) {
    var ds = Object.create(DataSocketO);
    ds.type = type;
    return ds
}