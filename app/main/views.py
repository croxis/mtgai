__author__ = 'croxis'
from datetime import datetime
import re
import urllib.parse

from flask import redirect, render_template, session, url_for
import lib.cardlib as cardlib

from . import main
from .. import magic_image
from .forms import SubmitCardsForm


@main.route('/')
def index():
    return redirect(url_for('.index_mtgai'))


@main.route('/mtgai', methods=['GET', 'POST'])
def index_mtgai():
    form = SubmitCardsForm()
    if form.validate_on_submit():
        session['card text'] = form.body.data
        return redirect(url_for('.card_select'))
    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form,
                           name='name',
                           title='MTG Automatic Inventor (MTGAI)')


@main.route('/mtgai/card-select', methods=['GET', 'POST'])
def card_select():
    #cards = convert_cards(session['card text'])[:6]  # Max 6 cards for testing
    urls = convert_to_urls(session['card text'])
    return render_template('card_select.html', urls=urls)


def convert_to_urls(card_text, cardsep='\r\n\r\n'):
    urls = []
    for card_src in card_text.split(cardsep):
        if card_src:
            card = cardlib.Card(card_src)
            if card.valid:
                urls.append(urllib.parse.quote(card_src, safe=''))

    return urls


def convert_cards(text, cardsep='\r\n\r\n'):
    """Card separation is \r\n\r\n when submitted by form and \n\n by text
    file."""
    cards = []
    for card_src in text.split(cardsep):
        if card_src:
            card = cardlib.Card(card_src)
            if card.valid:
                cards.append(card)
    return cards


def create_urls(cards):
    urls = []
    for card in cards:
        # Cost calculation
        cost = {}
        colorless = 0
        cost['white'] = card.cost.format().lower().count('w')
        cost['blue'] = card.cost.format().lower().count('u')
        cost['black'] = card.cost.format().lower().count('b')
        cost['red'] = card.cost.format().lower().count('r')
        cost['green'] = card.cost.format().lower().count('g')
        color = str(max(cost, key=cost.get))
        for key, value in cost.items():
            if value:
                break
        else:
            color = 'artifact'
        rg = re.compile('(\\d+)', re.IGNORECASE|re.DOTALL)
        m = rg.search(card.cost.format())
        if m:
            colorless = int(m.group(1))
        power = ''
        toughness = ''
        if card.types[0].lower() == 'creature':
            power = str(card.pt_p.count('^'))
            toughness = str(card.pt_t.count('^'))
        # Find an image
        terms = magic_image.find_search_terms(card.encode())
        img_url = ''
        for term in terms:
            #color = term[-1]
            query = "+".join(term[:-1])
            img_url = magic_image.fetch(query + '+"fantasy"+paintings+-card', color)
            if img_url:
                break
        url = "http://www.mtgcardmaker.com/mcmaker/createcard.php?name=" + \
              card.name.format(gatherer=True) + \
              "&color=" + color + \
              "&mana_r=" + str(cost['red']) + "&mana_u=" + str(cost['blue']) + \
              "&mana_g=" + str(cost['green']) + "&mana_b=" + str(cost['black']) + \
              "&mana_w=" + str(cost['white']) + "&mana_colorless=" + str(colorless) + \
              "&picture=" + urllib.parse.quote(img_url) + "&supertype=&cardtype=" + \
              card.types[0] + \
              "&subtype=&expansion=&rarity=Common&cardtext=" + \
              card.text.format() + \
              "&power=" + power + "&toughness=" + toughness + "&artist=&bottom=%E2%84%A2+%26+%C2%A9+1993-2016+Wizards+of+the+Coast+LLC&set1=&set2=&setname="
        urls.append(url)
    return urls

