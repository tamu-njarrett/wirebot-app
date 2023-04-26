from datetime import datetime, time
from sqlalchemy import update
from wirebot import db
from wirebot.models import Status, Buttons, RunTime

# update status message to Jetson to start wirebot operation
def run_wirebot():
    db.session.execute(update(Buttons), [{'id': 1, 'start': 1}])
    db.session.commit()

# update status message to Jetson to stop wirebot operation
def stop_wirebot():
    db.session.execute(update(Buttons), [{'id': 1, 'stop': 1}])
    db.session.commit()

# reset both button states to 0
def reset_buttons():
    db.session.execute(update(Buttons), [{'id': 1, 'start': 0}])
    db.session.execute(update(Buttons), [{'id': 1, 'stop': 0}])
    db.session.commit()

# Row (id) 1 of status SQL class holds boolean status code
# Each function updates the row with appropriate 1's or 0's
def reset_status():
    db.session.execute(
        update(Status),
        [
            {'id': 1, 'connection': 0},
            {'id': 1, 'capturing': 0},
            {'id': 1, 'rotating': 0},
            {'id': 1, 'shifting': 0},
            {'id': 1, 'finishing': 0},
            {'id': 1, 'row_num': 0},
        ],
    )
    db.session.commit()

def connection():
    db.session.execute(update(Status), [{'id': 1, 'connection': 1}])
    db.session.commit()

def capturing():
    db.session.execute(
        update(Status),
        [{'id': 1, 'capturing': 1},
         {'id': 1, 'rotating': 0},
         {'id': 1, 'shifting': 0},
        ],
    )
    db.session.commit()

def rotating():
    db.session.execute(
        update(Status),
        [
            {'id': 1, 'capturing': 0},
            {'id': 1, 'rotating': 1},
            {'id': 1, 'shifting': 0},
        ],
    )
    db.session.commit()

def shifting(row_count):
    db.session.execute(
        update(Status),
        [
            {'id': 1, 'capturing': 0},
            {'id': 1, 'rotating': 0},
            {'id': 1, 'shifting': 1},
            {'id': 1, 'row_num': row_count}
        ],
    )
    db.session.commit()

def finishing():
    db.session.execute(
        update(Status),
        [
            {'id': 1, 'capturing': 0},
            {'id': 1, 'rotating': 0},
            {'id': 1, 'shifting': 0},
            {'id': 1, 'finishing': 1},
            {'id': 1, 'row_num': 0},
        ],
    )
    db.session.commit()

# Set either start or stop time
def set_time(timer, start_or_stop):
    if start_or_stop == 'start':
        db.session.execute(update(RunTime), [{'id': timer.id, 'start_time': datetime.now()}])
    elif start_or_stop == 'stop':
        db.session.execute(update(RunTime), [{'id': timer.id, 'stop_time': datetime.now()}])
    db.session.commit()

# Calculate total run time
def calc_run_time(timer):
    total_run_time = timer.stop_time - timer.start_time
    total_seconds = int(total_run_time.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    run_time_h_m_s = time(hours, minutes, seconds)
    db.session.execute(update(RunTime), [{'id': timer.id, 'run_time': run_time_h_m_s}])
    db.session.commit()

    return run_time_h_m_s
