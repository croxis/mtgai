__author__ = 'croxis'

from io import BytesIO
import urllib.parse

from flask import send_file, request

import lib.cardlib as cardlib

from . import card_craft
from ..card_visual import create_card_img


@card_craft.route('/mtgai/card-craft/<path:raw>')
def index(raw):
    card = create_card(urllib.parse.unquote(raw))
    if request.args.get('no-google'):
        image = create_card_img(card, google=False)
    else:
        image = create_card_img(card, google=True)
    image.show()
    byte_io = BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')


def create_card(raw):
    return cardlib.Card(raw)


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
