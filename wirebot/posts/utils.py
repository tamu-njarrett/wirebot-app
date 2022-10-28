import os
import secrets
from wirebot import db
from wirebot.models import Post
from PIL import Image
from flask import current_app


# Saving picture to proile_pics directory and returning new file name "random hex".ext
def save_picture_post(form_picture, post):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)  # only need file extension, throwing away name
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/post_pics', picture_fn)

    # Update db with new picture name
    post.picture = picture_fn
    db.session.commit()
    
    # Resizing image to 256 x 256pixels using Pillow module
    output_size = 512, 512
    im = Image.open(form_picture)
    im.thumbnail(output_size)
    im.save(picture_path)
    
    return picture_fn