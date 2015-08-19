__author__ = 'croxis'
import os

from flask import Flask
from flask.ext.bootstrap import Bootstrap, WebCDN
from flask.ext.moment import Moment
from flask.ext.socketio import SocketIO
from flask_kvsession import KVSessionExtension

from simplekv.fs import FilesystemStore

from config import config

from .image_manager import ImageManager

bootstrap = Bootstrap()
moment = Moment()
socketio = SocketIO()
img_manager = ImageManager()
store = None
app = None


def create_app(config_name):
    global app, store  # I know I know globals bad.
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    try:
        os.makedirs(config[config_name].CACHE_PATH)
    except OSError:
        app.logger.debug("Cache path already generated")
    store = FilesystemStore(config[config_name].CACHE_PATH)

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    socketio.init_app(app)
    KVSessionExtension(store, app)


    app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
    '//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.4/')


    # Attach routes and custom error pages here
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .mtgcardcraft import card_craft as card_craft_blueprint
    app.register_blueprint(card_craft_blueprint)
    return app


def get_scocket():
    return socketio