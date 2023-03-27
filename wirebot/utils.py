import simple_websocket, os
from flask import request, current_app
from wirebot import db

# send TCP/IP message to Jetson to start wirebot operation
def run_wirebot(status):
    status_file_path = os.path.join(current_app.root_path, 'status_file.txt')
    with open(status_file_path, 'w') as status_file:
        status_file.write('new status=run')

    return status

# send TCP/IP message to Jetson to stop wirebot operation
def stop_wirebot(status):
    status_file_path = os.path.join(current_app.root_path, 'status_file.txt')
    with open(status_file_path, 'w') as status_file:
        status_file.write('new status=stop')

    return status

# send TCP/IP message to Jetson to transition to Row 1 / Row 2 / Row 3
def change_row_wirebot(status):
    status_file_path = os.path.join(current_app.root_path, 'status_file.txt')
    with open(status_file_path, 'w') as status_file:
        status_file.write('new status=change_row')

    return status

def send_status_update(status_update):
    ws = simple_websocket.Server(request.environ)
    if ws.connected:
        print('Connected, preparing to send status update...')
    try:
        while True:
            ws.send(f'status={status_update}')
            data = ws.receive()
            print(data)

    except simple_websocket.ConnectionClosed:
        print(f'Client disconnected, code: {ws.close_reason}')
        pass

    ws.close()

    return ''

