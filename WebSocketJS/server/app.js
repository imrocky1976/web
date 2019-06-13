// 依赖：
// 1、npm install socket.io
// 2、npm install express
// 运行：
// node app.js
var app = require('express')();
var server = require('http').createServer(app);
var io = require('socket.io').listen(server);

server.listen(7000);

app.get('/', function(req, res) {
    res.sendFile(__dirname + '/index.html');
});


io.sockets.on('connection', function (socket) {
    socket.emit('news', { hello: 'world' });
    socket.on('anotherNews', function (data) {
    console.log(data);
    });
   });
   