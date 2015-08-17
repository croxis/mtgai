__author__ = 'croxis'
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.socketio import SocketIO
from config import config

from .image_manager import ImageManager

bootstrap = Bootstrap()
moment = Moment()
socketio = None
img_manager = ImageManager()
app = None


def create_app(config_name):
    global app  # I know I know globals bad.
    global socketio
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    socketio = SocketIO(app)

    # Attach routes and custom error pages here
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .mtgcardcraft import card_craft as card_craft_blueprint
    app.register_blueprint(card_craft_blueprint)
    return app
    #return socketio


def get_scocket():
    return socketio