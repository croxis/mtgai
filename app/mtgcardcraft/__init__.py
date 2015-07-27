__author__ = 'croxis'
from flask import Blueprint

card_craft = Blueprint('card_craft', __name__)

from . import views, errors