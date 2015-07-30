__author__ = 'croxis'
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'a string that is hard to velociraptor'
    SNAPSHOTS_PATH = '~/char-rnn-master/brains'
    GENERATOR_PATH = '~/char-rnn-master/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
