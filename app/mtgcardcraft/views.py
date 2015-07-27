__author__ = 'croxis'
from datetime import datetime
from io import BytesIO
import re
import urllib.parse

from flask import redirect, render_template, session, url_for, send_file
from PIL import Image, ImageDraw, ImageFont

import lib.cardlib as cardlib

from . import card_craft
from .. import magic_image


@card_craft.route('/mtgai/card-craft/<path:raw>')
def index(raw):
    card = cardlib.Card(urllib.parse.unquote(raw))
    # Cost calculation
    cost = {}
    cost['colorless'] = 0
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
    rg = re.compile('(\\d+)', re.IGNORECASE | re.DOTALL)
    m = rg.search(card.cost.format())
    if m:
        cost['colorless'] = int(m.group(1))

    # image = Image.open("app/card_parts/magic-new.mse-style/acard.jpg")
    if color == 'blue':
        color = 'u'
    image = Image.open("app/card_parts/magic-new.mse-style/" +
                       color[0] +
                       "card.jpg")
    # Card texts
    font = ImageFont.truetype("fonts/matrixb.ttf", size=20)
    draw = ImageDraw.Draw(image)
    draw.text((35, 35),
              card.name.format(gatherer=True),
              fill=(0, 0, 0, 255),
              font=font)
    draw.text((35, 300), card.types[0], fill=(0, 0, 0, 255), font=font)
    draw.multiline_text((35, 335), card.text.format(), fill=(0, 0, 0, 255), font=font)
    draw.text((60, 484), "Copy, right?", fill=(0, 0, 0, 255), font=font)

    # Card costs
    red_mana = Image.open('app/card_parts/magic-mana-beveled.mse-symbol-font/mana_r.png')
    green_mana = Image.open('app/card_parts/magic-mana-beveled.mse-symbol-font/mana_g.png')
    black_mana = Image.open('app/card_parts/magic-mana-beveled.mse-symbol-font/mana_b.png')
    blue_mana = Image.open('app/card_parts/magic-mana-beveled.mse-symbol-font/mana_u.png')
    white_mana = Image.open('app/card_parts/magic-mana-beveled.mse-symbol-font/mana_w.png')
    colorless_mana = Image.open('app/card_parts/magic-mana-beveled.mse-symbol-font/mana_circle.png')
    red_mana.thumbnail((25, 25))
    green_mana.thumbnail((25, 25))
    black_mana.thumbnail((25, 25))
    blue_mana.thumbnail((25, 25))
    white_mana.thumbnail((25, 25))
    colorless_mana.thumbnail((25, 25))

    offset = 0
    for x in range(0, cost['white']):
        image.paste(white_mana, (320 - offset, 29), white_mana)
        offset += 25
    for x in range(0, cost['blue']):
        image.paste(blue_mana, (320 - offset, 29), white_mana)
        offset += 25
    for x in range(0, cost['black']):
        image.paste(black_mana, (320 - offset, 29), white_mana)
        offset += 25
    for x in range(0, cost['green']):
        image.paste(green_mana, (320 - offset, 29), white_mana)
        offset += 25
    for x in range(0, cost['red']):
        image.paste(red_mana, (320 - offset, 29), white_mana)
        offset += 25
    if cost['colorless']:
        draw_colorless = ImageDraw.Draw(colorless_mana)
        draw_colorless.text((8, 4), str(cost['colorless']), fill=(0, 0, 0, 255), font=font)
        image.paste(colorless_mana, (320 - offset, 29), colorless_mana)

    byte_io = BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')


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
