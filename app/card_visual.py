__author__ = 'croxis'
from io import BytesIO
import random
import re

from PIL import Image, ImageDraw, ImageFont
import requests

import lib.transforms as transforms
import lib.utils as utils
from lib.manalib import Manatext

from . import magic_image
from . import img_manager

try:
    import textwrap
    import nltk.data
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    # This crazy thing is actually invoked as an unpass, so newlines are still
    # encoded.
    def sentencecase(s):
        s = s.replace(utils.x_marker, utils.reserved_marker)
        lines = s.split(utils.newline)
        clines = []
        for line in lines:
            if line:
                sentences = sent_tokenizer.tokenize(line)
                clines += [' '.join([sent.capitalize() for sent in sentences])]
        return utils.newline.join(clines).replace(utils.reserved_marker, utils.x_marker)
except ImportError:
    def sentencecase(s):
        return s.capitalize()


def create_card_img(card, google):
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
    colors = 0
    for key, value in cost.items():
        if value:
            colors += 1
    if colors > 1:
        color = 'multicolor'

    rg = re.compile('(\\d+)', re.IGNORECASE | re.DOTALL)
    m = rg.search(card.cost.format())
    if m:
        cost['colorless'] = int(m.group(1))

    image = img_manager.get_background(color)
    font_title = ImageFont.truetype("fonts/beleren-bold_P1.01.ttf", size=18)
    font_type = ImageFont.truetype("fonts/beleren-bold_P1.01.ttf", size=16)
    font = ImageFont.truetype("fonts/mplantin.ttf", size=18)
    draw = ImageDraw.Draw(image)
    w, h = img_manager.get_icon('white').size
    # Card costs
    x_offset = 0
    for x in range(0, cost['white']):
        image.paste(img_manager.get_icon('white'),
                    (321 - x_offset, 42 - h // 2),
                    img_manager.get_icon('white'))
        x_offset += 23
    for x in range(0, cost['blue']):
        image.paste(img_manager.get_icon('blue'),
                    (321 - x_offset, 42 - h // 2),
                    img_manager.get_icon('blue'))
        x_offset += 23
    for x in range(0, cost['black']):
        image.paste(img_manager.get_icon('black'), (321 - x_offset, 42 - h // 2),
                    img_manager.get_icon('blue'))
        x_offset += 23
    for x in range(0, cost['green']):
        image.paste(img_manager.get_icon('green'), (321 - x_offset, 42 - h // 2),
                    img_manager.get_icon('blue'))
        x_offset += 23
    for x in range(0, cost['red']):
        image.paste(img_manager.get_icon('red'), (321 - x_offset, 42 - h // 2),
                    img_manager.get_icon('blue'))
        x_offset += 23
    if cost['colorless']:
        colorless_mana = img_manager.get_icon('colorless')
        draw_colorless = ImageDraw.Draw(colorless_mana)
        w, h = draw_colorless.textsize(str(cost['colorless']))
        W, H = colorless_mana.size
        draw_colorless.text(((W-w) // 2 - 2, (H-h) // 2 - 5),
                            str(cost['colorless']),
                            fill=(0, 0, 0, 255),
                            font=font_title)
        image.paste(colorless_mana,
                    (321 - x_offset, 36 - h // 2),
                    colorless_mana)
        colorless_mana.close()

    # Card texts
    w, h = draw.textsize(card.name.title())
    draw.text((35, 38 - h // 2),
              # card.name.format(gatherer=True),
              card.name.title(),
              fill=(0, 0, 0, 255),
              font=font_title)
    if 'creature' in card.types:
        w, h = draw.textsize(' '.join(card.types).title() + ' - ' + ' '.join(card.subtypes).title())
        draw.text((35, 304-h//2),
                  ' '.join(card.types).title() + ' - ' + ' '.join(card.subtypes).title(),
                  fill=(0, 0, 0, 255),
                  font=font_type)
    else:
        w, h = draw.textsize(' '.join(card.types).title())
        draw.text((35, 304-h/2),
                  ' '.join(card.types).title(),
                  fill=(0, 0, 0, 255),
                  font=font_type)
    # card_text = card.text.format()
    mtext = card.text.text
    mtext = transforms.text_unpass_1_choice(mtext, delimit=True)
    mtext = transforms.text_unpass_2_counters(mtext)
    mtext = transforms.text_unpass_3_unary(mtext)
    mtext = transforms.text_unpass_4_symbols(mtext, for_forum=False)
    mtext = sentencecase(mtext)
    # We will do step 5 ourselves to keep capitalization
    mtext = transforms.text_unpass_5_cardname(mtext, card.name.title())
    mtext = transforms.text_unpass_6_newlines(mtext)
    new_text = Manatext('')
    new_text.text = mtext
    new_text.costs = card.text.costs
    card_text = new_text.format()
    lines = textwrap.wrap(card_text, 37, replace_whitespace=False)
    y_offset = 0
    for line in lines:
        for sub_line in line.split('\n'):
            x_offset = 0
            rg = re.compile('(\\{.*?\\})', re.IGNORECASE | re.DOTALL)
            for subsub_line in rg.split(sub_line):
                if subsub_line:
                    if rg.match(subsub_line):
                        if '{w}' in subsub_line.lower():
                            image.paste(img_manager.get_icon_text('white'),
                                        (35 + x_offset, 335 + y_offset - 3),
                                        img_manager.get_icon_text('blue'))
                            x_offset += 21
                        elif '{b}' in subsub_line.lower():
                            image.paste(img_manager.get_icon_text('black'),
                                        (35 + x_offset, 335 + y_offset - 3),
                                        img_manager.get_icon_text('blue'))
                            x_offset += 21
                        elif '{u}' in subsub_line.lower():
                            image.paste(img_manager.get_icon_text('blue'),
                                        (35 + x_offset, 335 + y_offset - 3),
                                        img_manager.get_icon_text('blue'))
                            x_offset += 21
                        elif '{r}' in subsub_line.lower():
                            image.paste(img_manager.get_icon_text('red'),
                                        (35 + x_offset, 335 + y_offset - 3),
                                        img_manager.get_icon_text('blue'))
                            x_offset += 21
                        elif '{g}' in subsub_line.lower():
                            image.paste(img_manager.get_icon_text('green'),
                                        (35 + x_offset, 335 + y_offset - 3),
                                        img_manager.get_icon_text('blue'))
                            x_offset += 21
                        elif '{t}' in subsub_line.lower():
                            image.paste(img_manager.get_icon_text('tap'),
                                        (35 + x_offset, 335 + y_offset - 3),
                                        img_manager.get_icon_text('tap'))
                            x_offset += 21
                        else:
                            try:
                                int(subsub_line[1])
                                colorless_mana = img_manager.get_icon_text('colorless')
                                draw_colorless = ImageDraw.Draw(colorless_mana)
                                w, h = draw_colorless.textsize(str(subsub_line[1]))
                                draw_colorless.text(((18-w) // 2, (18-h) // 2 - 3),
                                                    str(subsub_line[1]),
                                                    fill=(0, 0, 0, 255),
                                                    font=font_title)

                                image.paste(colorless_mana,
                                        (35 + x_offset, 335 + y_offset - 3),
                                        colorless_mana)
                                colorless_mana.close()
                                x_offset += 21
                            except:
                                pass
                    else:
                        draw.text((35 + x_offset, 335 + y_offset),
                                  subsub_line,
                                  fill=(0, 0, 0, 255),
                                  font=font)
                        x_offset += font.getsize(subsub_line)[0]
            y_offset += 20

    draw.text((60, 484), "Copy, right?", fill=(0, 0, 0, 255), font=font)

    # Creature power
    for card_type in card.types:
        if card_type.lower() == 'creature':
            power = str(card.pt_p.count('^'))
            toughness = str(card.pt_t.count('^'))
            c = color[0]
            if color.lower() == 'blue':
                c = 'u'
            pt_image = Image.open('app/card_parts/magic-new.mse-style/' +
                                  c +
                                  'pt.jpg')
            image.paste(pt_image, (271, 461))
            draw.text((295, 470), power + " / " + toughness, fill=(0, 0, 0, 255),
                      font=font_title)

    # Card image
    art, w, h = get_card_art(card, google)
    image.paste(art, ((image.size[0] - w) // 2, 175-h//2))
    return image

def get_card_art(card, google):
    if google:
        google_result=google_card_art(card)
        if google_result!=None:
            return google_result
    return get_default_card_art(card)

def get_default_card_art(card):
    art = img_manager.default_portrait
    art = art.crop((0, 0, 311, 228))
    w, h = art.size
    return (art, w, h)

def google_card_art(card):
    terms = magic_image.find_search_terms(card)
    random.shuffle(terms)
    img_url = None
    for term in terms[:5]:
        color = term[-1]
        query = "+".join(term[:-1])
        if color == 'u':
            color = 'blue'
        img_url = magic_image.fetch(query + '+"fantasy"+paintings+-card', color)
        if img_url:
            break
    if img_url:
        with BytesIO(requests.get(img_url).content) as reader:
            reader.seek(0)
            art = Image.open(reader)
            art.thumbnail((311, 311))
            art = art.crop((0, 0, 311, 228))
            w, h = art.size
            return (art, w, h)
    return None
