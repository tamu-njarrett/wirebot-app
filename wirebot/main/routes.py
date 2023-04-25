from . import main
from datetime import datetime
from flask import render_template, request
from wirebot import db
from wirebot.models import Post, Buttons, Status, RunTime
from wirebot.utils import reset_buttons, reset_status, connection, capturing, rotating, shifting, finishing, set_time, calc_run_time
import simple_websocket


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


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
