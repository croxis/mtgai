__author__ = 'croxis'
from flask import render_template
from . import card_craft

@card_craft.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@card_craft.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

