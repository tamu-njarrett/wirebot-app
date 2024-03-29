from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy import MetaData
from turbo_flask import Turbo
#from flask_socketio import SocketIO
from wirebot.config import Config


# App factory
db = SQLAlchemy(metadata=MetaData(naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
}))
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'  # bootstrap: must be logged in reach account route
login_manager.login_message_category = 'info'   # bootstrap: flash message for logging in
mail = Mail()
turbo = Turbo()


def create_app(config_class=Config, debug=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.debug = debug

    db.init_app(app)
    migrate.init_app(app, db)   # for updating models
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    turbo.init_app(app)

    # Importing Blueprints
    from wirebot.users.routes import users    # importing instance of Blueprint
    from wirebot.posts.routes import posts
    from wirebot.main.routes import main
    from wirebot.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    
#    sio.init_app(app)

    return app
