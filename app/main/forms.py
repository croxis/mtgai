from flask_wtf import Form
from wtforms import SubmitField, TextAreaField
from wtforms.validators import Required

__author__ = 'croxis'


class SubmitCardsForm(Form):
    body = TextAreaField("Copy and paste card data here.", validators=[Required()])
    submit = SubmitField("Submit")