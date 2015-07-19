__author__ = 'croxis'
from datetime import datetime
from flask import redirect, render_template, session, url_for
import lib.cardlib as cardlib

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
    cards = convert_cards(session['card text'])[:9]  # Max 9 cards for testing
    urls = create_urls(cards)
    return render_template('card_select.html', cards=cards, urls=urls)


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

def create_urls(cards):
    urls = []
    for card in cards:
        url = "http://www.mtgcardmaker.com/mcmaker/createcard.php?name=" + \
              card.name + \
              "&color=White&mana_r=1&mana_u=2&mana_g=0&mana_b=0&mana_w=0&mana_colorless=3&picture=http%3A%2F%2Fwww.permaculture.co.uk%2Fsites%2Fdefault%2Ffiles%2Fimages%2Fgreek-potato.standard%2520460x345.gif&supertype=&cardtype=" + \
              card.types[0] + \
              "&subtype=&expansion=&rarity=Common&cardtext=" + \
              card.text.format() + \
              "&power=&toughness=&artist=&bottom=%E2%84%A2+%26+%C2%A9+1993-2016+Wizards+of+the+Coast+LLC&set1=&set2=&setname="
        urls.append(url)
    return urls

