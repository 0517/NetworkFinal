
var client = {
    control_socket: null,
    data_socket: null,

    makeSound: function(){ alert("喵喵喵"); }
};

$(document).ready(function(){
    $(".btn-login").click(function() {
        ControlConnect();
    });
});

function ControlConnect() {

}