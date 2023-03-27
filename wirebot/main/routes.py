from . import main
from flask import render_template, request, current_app
from wirebot import db
from wirebot.models import Post
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

@main.route('/echo', websocket=True)
def echo():
    ws = simple_websocket.Server(request.environ, ping_interval=25)
    if ws.connected:
        print('Connected, preparing to send status update...')

    try:
        while True:
            status_file_path = os.path.join(current_app.root_path, 'status_file.txt')
            with open(status_file_path, 'r') as status_file:
                current_command = status_file.read()
                if 'new' in current_command:
                    c_new, command = current_command.split()
                    ws.send(command)        # sending update command
                    data = ws.receive()     # receiving acknowledge
                    if 'status' in data:
                        print(f'Actual status: {data}')
                    else:
                        print(f'Other message received: {data}')
                        
                    with open(status_file_path, 'w') as status_file:
                        status_file.write(f'old {command}')

            # if ws.receive():
            #     data = ws.receive()
            #     if 'status' in data:
            #         print(f'Wirebot actual status: {data}')
            #     else:
            #         print(f'Other message received: {data}')

    except simple_websocket.ConnectionClosed:
        print(f'Clinet disconnected, code: {ws.close_reason}')

    return ''

    # ws = simple_websocket.Server(request.environ, ping_interval=25)
    # if ws.connected:
    #     print('Client connected')
    # try:
    #     while True:
    #         data = ws.receive()
    #         if 'status' in data:
    #             print(f'{data}')
    #             ws.send('status update acknowledged')

    #         else:
    #             print(f'other message: {data}')
    #             ws.send('message acknowledged')

    # except simple_websocket.ConnectionClosed:
    #     print(f'Client disconnected, code: {ws.close_reason}')
    #     pass