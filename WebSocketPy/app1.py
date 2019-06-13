from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import datetime
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

thread = None
thread_lock = threading.Lock()

def thread_func():
    while True:
        t = datetime.datetime.now()
        socketio.emit('curtime', {'date': '%d:%d:%d' % (t.year, t.month, t.day), 
            'time': '%d:%d:%d' % (t.hour, t.minute, t.second)}, namespace='/showtime')
        print(t)
        socketio.sleep(0.5)


@app.route('/')
def index():
    return render_template('index1.html')

@socketio.on('connect', namespace='/showtime')
def connect():
    print('a socket client connected.')
    emit('my response', {'data': 'Connected'})

@socketio.on('showtime', namespace='/showtime')
def show_time():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(thread_func)

@socketio.on('disconnect', namespace='/showtime')
def disconnect():
    print('disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=7000)