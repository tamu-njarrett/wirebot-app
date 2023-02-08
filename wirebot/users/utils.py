import os, secrets, time
from PIL import Image
from flask import url_for, render_template, current_app
from flask_mail import Message
from wirebot import mail, turbo


# Saving picture to proile_pics directory and returning new file name "random hex".ext
def save_picture_user(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)  # only need file extension, throwing away name
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    # Resizing image to 128 x 128 pixels using Pillow module
    output_size = 128, 128
    im = Image.open(form_picture)
    im.thumbnail(output_size)
    im.save(picture_path)
    
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Greenhouse Wirebot Password Reset', sender=('Greenhouse Wirebot','noreply@greenhousewirebot.com'), recipients=[user.email])
    msg.body = f'''Please follow the link to reset your password:
    {url_for('users.reset_token', token=token, _external=True)}
    
    If you didn't make this request, simply ignore this email.
    '''
    mail.send(msg)

# FIX USER SPECIFIC UPDATES
# @turbo.user_id
# def get_current_user_id():
#     return current_user.id

# updating values on dashboard every 5 seconds
# can update specific clients with @turbo.user_id decorator (obtained from Flask-Login current_user)
def update_dashboard(app):
    with app.app_context():
        while True:
            time.sleep(5)
            turbo.push(turbo.replace(render_template('dashboard_values.html'), 'dashboard_values'))    # sending update to all connected clients