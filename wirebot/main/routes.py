from . import main
from flask import render_template, request, current_app
from sqlalchemy import select, update
from wirebot import db
from wirebot.models import Post, Status, Buttons
from wirebot.utils import reset_buttons, reset_status, connection, capturing, rotating, shifting, finishing
import simple_websocket, os



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
        reset_buttons   # reset button states
        
    # Handshake loop with Jetson
    while True:
        data = ws.receive(0)
        if data == 'handshake':
            ws.send('ready')
            connection()    # update connection status
            break

    try:
        while True:
            stop_pressed = Buttons.query.filter_by(id=1).first().stop
            if stop_pressed == True:
                ws.send('status=stop')
                db.session.execute(update(Buttons), [{'id': 1, 'stop': 0}])
                db.session.commit()

            else:
                data = ws.receive(0)
                if data == 'capturing':
                    capturing()
                elif data == 'rotating':
                    rotating()
                elif data == 'shifting':
                    shifting()
                elif data == 'finishing':
                    finishing
                    

    except simple_websocket.ConnectionClosed:
        print(f'Client disconnected, code: {ws.close_reason}')
        reset_status()

    ws.close()
    reset_status()

    return ''
