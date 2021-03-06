
$(document).ready(function(){
    var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
    var current_char = 0;
    var max_char = 0;
    var percent = 0;
    socket.emit('generate');
    socket.on('set max char', function(msg) {
        max_char = msg.data;
    });
    socket.on('raw card', function(msg) {
        $('#raw-cards').append('<p>' + msg.data + '</p>');
        current_char += msg.data.length;
        console.log('Log (' + current_char + '/' + max_char +'): ' + msg.data);
        percent = current_char/max_char*100
        if (percent>100) {
            percent = 100;
        }
        $('#raw-progress').css('width', percent + '%').attr('aria-valuenow', current_char).html(+percent.toFixed(2) + '%');
    });
    socket.on('text card', function(msg) {
        var arrayLength = msg.data.length;
        for (var i = 0; i< arrayLength; i++){
            $('#text-cards').append('<div>' + msg.data[i] + '</div>');
        }
        console.log('Log (text-card): ' + msg.data);
    });
    socket.on('image card', function(msg) {
        console.log('Log (image-card): ' + msg.data);
        $('#image-cards').append('<div class="col-md-4"><img style="padding:3px;" src="card-craft/'+ msg.data +'"></div>');
    });
    socket.on('ping', function(msg) {
        console.log('Ping: ' + msg.data);
    });
    socket.on('finished generation', function(msg) {
        console.log('Finished card generation');
        $('#raw-progress').css('width', '100%').attr('aria-valuenow', current_char).html('100%');
        $('#raw-progress').removeClass('active');
    });
    //socket.on('connect', function() {
    //    socket.emit('my event', {data: 'I\'m connected!'});
    //});
    // start up the SocketIO connection to the server - the namespace 'test' is also included here if necessary
    //var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    // this is a callback that triggers when the "my response" event is emitted by the server.
    //socket.on('my response', function(msg) {
    //    $('#log').append('<p>Received: ' + msg.data + '</p>');
    //    console.log('Log: ' + msg.data);
    //});
    //example of triggering an event on click of a form submit button
    //$('form#emit').submit(function(event) {
    //    socket.emit('my event', {data: $('#emit_data').val()});
    //    return false;
    //});
});
