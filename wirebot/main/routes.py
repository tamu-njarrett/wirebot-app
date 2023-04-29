from . import main
from datetime import datetime, time
from flask import render_template, request
from flask_login import login_required
from wirebot import db
from wirebot.models import Post, Buttons, RunTime
from wirebot.utils import reset_buttons, reset_status, connection, capturing, rotating, shifting, finishing, set_time, calc_run_time
import simple_websocket


@main.route("/")
@main.route("/home")
def home():
    # Home page pictures
    greenhouse = 'greenhouse.JPG'
    integrated_system = 'integrated_system.jpg'
    return render_template('home.html', greenhouse=greenhouse, integrated_system=integrated_system)


@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route('/status', websocket=True)
def status():
    ws = simple_websocket.Server(request.environ, ping_interval=25) # instantiate websocket class
    if ws.connected:
        print('Connected, preparing to send status update...')
        reset_status()  # resetting all status types 
        reset_buttons()   # reset button states
        row_count = 0   # set row count to 0
        timer = RunTime(start_time=datetime(year=1,month=1,day=1,hour=0,minute=0,second=0), stop_time=datetime(year=1,month=1,day=1,hour=0,minute=0,second=0))   # add a new entry for run time
        db.session.add(timer)
        db.session.commit()
        
    # Handshake loop with Jetson
    while True:
        data = ws.receive(0)
        if data == 'handshake':
            ws.send('ready')
            connection()    # update connection status
            set_time(timer, 'start')    # add start time
            break

    try:
        while True:
            stop_pressed = Buttons.query.filter_by(id=1).first().stop
            if stop_pressed == True:
                ws.send('status=stop')
                print('Stop button pressed')
                button_stop_time = datetime.now()
                reset_buttons()

            else:
                data = ws.receive(0)
                if data == 'capturing':
                    capturing()
                elif data == 'rotating':
                    rotating()
                elif data == 'shifting':
                    row_count += 1
                    shifting(row_count)
                elif data == 'finishing':
                    finishing()
                elif data == 'stopped':
                    jetson_stop_time = datetime.now()
                    stop_timer = jetson_stop_time - button_stop_time
                    print(f'Stop button timer: {stop_timer}')



    # Once Jetson disconnets, status is zeroed out
    except simple_websocket.ConnectionClosed:
        print(f'Client disconnected, code: {ws.close_reason}')
        set_time(timer, 'stop') # add stop time
        total_run_time = calc_run_time(timer)
        reset_status()
        print(f'Total run time: {total_run_time}')

    ws.close()
    reset_status()

    return ''

@main.route("/run_times")
@login_required
def run_times():
    run_times = RunTime.query.all()

    return render_template('run_times.html', title='Historic Run Times', run_times=run_times)