import time
from wirebot import db

# send TCP/IP message to Jetson to start wirebot operation
def run_wirebot(status):


    db.session.commit()
    time.sleep(5)


# send TCP/IP message to Jetson to stop wirebot operation
def stop_wirebot(status):

    return status