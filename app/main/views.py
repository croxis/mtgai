__author__ = 'croxis'
from datetime import datetime
from flask import redirect, render_template, session, url_for
import lib.cardlib as cardlib
import lib.utils as utils

from . import main
from .forms import SubmitCardsForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = SubmitCardsForm()
    if form.validate_on_submit():
        session['card text'] = form.body.data
        return redirect(url_for('.card_select'))
    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form,
                           name='name',
                           title='MTG Automatic Inventor (MTGAI)')


@main.route('/card-select', methods=['GET', 'POST'])
def card_select():
    cards = convert_cards(session['card text'])
    return render_template('card_select.html', cards=cards)


def convert_cards(text, cardsep='\r\n\r\n'):
    '''Card seperation is \r\n\r\n when submitted by form and \n\n by text
    file.'''
    cards = []
    for card_src in text.split(cardsep):
        if card_src:
            card = cardlib.Card(card_src)
            print(dir(card))
            if card.valid:
                cards.append(card)
    return cards
