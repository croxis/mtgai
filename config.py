__author__ = 'croxis'
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'a string that is hard to velociraptor'
    WTF_CSRF_SECRET_KEY = os.environ.get(
        'WTF_CSRF_SECRET_KEY') or 'a string that is hard to velociraptor'
    SNAPSHOTS_PATH = '~/char-rnn-master/brains'
    GENERATOR_PATH = '~/char-rnn-master/'
    GPU = -1  # Set to 0 if the machine will use the gpu to generate cards.
    LENGTH_LIMIT = 10000  # Limit number of characters generated.

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
