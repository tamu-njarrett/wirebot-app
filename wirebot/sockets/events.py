from flask_socketio import emit
from wirebot import socketio


# Decorator for SocketIO events
@socketio.event
def connect(sid, environ):
    print(sid, 'connected')

@socketio.event
def disconnect(sid):
    print(sid, 'disconnected')

@socketio.event
def message(data):
    print('Message received: ' + data)
