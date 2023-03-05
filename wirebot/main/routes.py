from . import main
from flask import render_template, request, Blueprint
from wirebot.models import Post
import simple_websocket, time



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
    ws = simple_websocket.Server(request.environ)
    if ws.connected:
        print('Client connected')
    try:
        while True:
            data = ws.receive()
            if 'status' in data:
                print(f'{data}')
                ws.send('status update acknowledged')

            else:
                print(f'other message: {data}')
                ws.send('message acknowledged')

    except simple_websocket.ConnectionClosed:
        print(f'Client disconnected, code: {ws.close_reason}')
        pass

    return ''