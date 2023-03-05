# from wirebot import sio
# from flask import request, session
# from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
# from threading import Lock
# from datetime import datetime
# import random, time, socket, sys


# @sio.event
# def connect(sid):
#     print(f'Connected: {request.sid}')
#     sio.emit('hello', (1, 2, {'Handshake': 'complete'}))

# # Receiving status update
# @sio.event
# def status_update(data):
#     print('From client: ', data)

# @sio.event
# def disconnect(sid):
#     print('Disconnect ', sid)