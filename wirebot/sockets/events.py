from flask import Blueprint
from flask_socketio import emit

sockets = Blueprint('sockets', __name__)

# Decorator for SocketIO events
@sockets.on('connect')
def connect():
    emit('after connect', {'data':'Howdy'})
    print('Client device connected')

@sockets.on('disconnect')
def disconnect():
    print('Client device disconnected')