from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from sqlalchemy import ForeignKey
from wirebot import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod  # self parameter not an argument
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token, expires_sec)['user_id']
        except:  
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(30), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    picture = db.Column(db.String(30), nullable=True)
    location = db.relationship('Location', backref='photo_taken_at_loc', lazy=True)

    def __repr__(self):
        return f"Photo('{self.date_uploaded}', '{self.location}')"


# Update to current wirebot status
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    connection = db.Column(db.Boolean, nullable=False)  # if network connection: 1, else: 0
    capturing = db.Column(db.Boolean, nullable=False) # moving down paracord
    rotating = db.Column(db.Boolean, nullable=False) # moving gimbal
    shifting = db.Column(db.Boolean, nullable=False) # moving down aisles
    finishing = db.Column(db.Boolean, nullable=False) # uploading pictures
    row_num = db.Column(db.Integer, nullable=True) # keeping count of row

    def __repr__(self):
        return f"Status('{self.connection}','{self.capturing}','{self.finishing}')"
    
class RunTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=True)
    stop_time = db.Column(db.DateTime, nullable=True)
    run_time = db.Column(db.Time, nullable=True)

    def __repr__(self):
        return f"RunTime('{self.start_time}','{self.stop_time}')"

class Buttons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Boolean, nullable=False) # if start button pressed
    stop = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Buttons('{self.start}', '{self.stop}')"

# Location of wirebot
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payload_loc = db.Column(db.Integer, nullable=False)
    horizontal_loc = db.Column(db.Integer, nullable=False)
    picture_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)    # referencing where picture is taken
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)

    def __repr__(self):
        return f"Location('{self.payload_loc}','{self.horizontal_loc}')"