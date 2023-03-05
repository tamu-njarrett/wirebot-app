import time, simple_websocket
from wirebot import db



# send TCP/IP message to Jetson to start wirebot operation
def run_wirebot(status):
    with open('status_file.txt', 'w') as status_file:
        status_file.write('status=run')

    return status


# send TCP/IP message to Jetson to stop wirebot operation
def stop_wirebot(status):
    with open('status_file.txt', 'w') as status_file:
        status_file.write('status=stop')

    return status

# send TCP/IP message to Jetson to transition to Row 1 / Row 2 / Row 3
def change_row_wirebot(status):
    with open('status_file.txt', 'w') as status_file:
        status_file.write('status=change_row')

    return status

