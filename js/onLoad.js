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
            client.ip();
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

    $('#Modify').on('click', function () {
        var $btn = $(this).button('loading');
        client.modifyIp($("#ip-id").val(), $("#new-ip").val());

    });

    $('#addButton').on('click', function () {

        var $btn = $(this).button('loading');
        client.addIp($('#create').val());

    });

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
        if (client.currentPwd.length == 1){
            $.scojs_message('Already root folder', $.scojs_message.TYPE_ERROR);
        } else {
            client.cwd('..');
        }
    });


});