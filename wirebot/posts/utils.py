import os
import secrets
from wirebot import db
from wirebot.models import Photo
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

##### Implement for loop for list of picture files ####
def save_picture_plant(picture_list):
    photo_object_list = []*len(picture_list)
    for pic in picture_list:
        current_photo = Photo()
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(pic.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.root_path, 'static/crop_pics', picture_fn)

        # update db
        current_photo.picture = picture_fn
        db.session.commit()

        # Scaling image
        im = Image.open(pic)
        im = im.resize((500, 500))
        im.save(picture_path)

        photo_object_list.append(current_photo)

    return photo_object_list

# Saving picture to database and static folder for display on Pictures View
def save_picture_ftp():

    photo_object_list = []
    photos = Photo.query.order_by(Photo.date_uploaded.desc())

    os.chdir("H:\\Documents\\2022 Fall\\ECEN 403\\code\\ftp-test")
    contents = os.listdir()

    # Grabbing list of new photos from current directory
    for file in contents:
        unique_photo = True
        f_name, f_ext = os.path.splitext(file)
        if f_ext == ('.JPG' or '.jpg' or '.PNG' or '.png' or '.HEIC'):
            for pic in photos:
                if file == pic.picture:
                    unique_photo = False

            if unique_photo:
                new_photo = Photo()
                picture_path = os.path.join(current_app.root_path, 'static/crop_pics', file)

                # Update db
                new_photo.picture = file
                db.session.commit()

                # Image magic
                im = Image.open(file)
                im = im.resize((500,500))
                im.save(picture_path)

                photo_object_list.append(new_photo)

    return photo_object_list

