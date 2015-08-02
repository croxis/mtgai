__author__ = 'croxis'
from io import BytesIO
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


def create_card_img(card):
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

    image = img_manager.get_background(color)
    #font = ImageFont.truetype("fonts/matrixb.ttf", size=20)
    font = ImageFont.truetype("fonts/MatrixBold.ttf", size=20)
    draw = ImageDraw.Draw(image)

    # Card costs
    y_offset = 0
    for x in range(0, cost['white']):
        image.paste(img_manager.get_icon('white'),
                    (320 - y_offset, 29),
                    img_manager.get_icon('white'))
        y_offset += 25
    for x in range(0, cost['blue']):
        image.paste(img_manager.get_icon('blue'),
                    (320 - y_offset, 29),
                    img_manager.get_icon('blue'))
        y_offset += 25
    for x in range(0, cost['black']):
        image.paste(img_manager.get_icon('black'), (320 - y_offset, 29),
                    img_manager.get_icon('blue'))
        y_offset += 25
    for x in range(0, cost['green']):
        image.paste(img_manager.get_icon('green'), (320 - y_offset, 29),
                    img_manager.get_icon('blue'))
        y_offset += 25
    for x in range(0, cost['red']):
        image.paste(img_manager.get_icon('red'), (320 - y_offset, 29),
                    img_manager.get_icon('blue'))
        y_offset += 25
    if cost['colorless']:
        colorless_mana = img_manager.get_icon('colorless')
        draw_colorless = ImageDraw.Draw(colorless_mana)
        draw_colorless.text((8, 4),
                            str(cost['colorless']),
                            fill=(0, 0, 0, 255),
                            font=font)
        image.paste(colorless_mana,
                    (320 - y_offset, 29),
                    colorless_mana)
        colorless_mana.close()

    # Card texts
    draw.text((35, 35),
              # card.name.format(gatherer=True),
              card.name.title(),
              fill=(0, 0, 0, 255),
              font=font)
    draw.text((35, 300), card.types[0].title(), fill=(0, 0, 0, 255), font=font)
    # card_text = card.text.format()
    mtext = card.text.text
    mtext = transforms.text_unpass_1_choice(mtext, delimit=True)
    mtext = transforms.text_unpass_2_counters(mtext)
    mtext = transforms.text_unpass_3_unary(mtext)
    mtext = transforms.text_unpass_4_symbols(mtext, for_forum=False)
    #mtext = transforms.text_unpass_4_symbols(mtext, for_forum=True)
    mtext = sentencecase(mtext)
    # We will do step 5 ourselves to keep capitalization
    mtext = transforms.text_unpass_5_cardname(mtext, card.name)
    mtext = transforms.text_unpass_6_newlines(mtext)
    new_text = Manatext('')
    new_text.text = mtext
    new_text.costs = card.text.costs
    card_text = new_text.format()
    #card_text = card_text.capitalize() # Before we inset title to preserve title caps
    #card_text = card_text.replace('@', card.name.title())
    #card_text = card_text.replace('\\', '\n')

    lines = textwrap.wrap(card_text, 36, replace_whitespace=False)
    y_offset = 0
    for line in lines:
        for sub_line in line.split('\n'):
            x_offset = 0
            rg = re.compile('(\\{.*?\\})', re.IGNORECASE | re.DOTALL)
            for subsub_line in rg.split(sub_line):
                if subsub_line:
                    if rg.match(subsub_line):
                        if '{w}' in subsub_line.lower():
                            image.paste(img_manager.get_icon('white'),
                                        (35 + x_offset, 335 + y_offset - 5),
                                        img_manager.get_icon('blue'))
                            x_offset += 25
                        elif '{b}' in subsub_line.lower():
                            image.paste(img_manager.get_icon('black'),
                                        (35 + x_offset, 335 + y_offset - 5),
                                        img_manager.get_icon('blue'))
                            x_offset += 25
                        elif '{u}' in subsub_line.lower():
                            image.paste(img_manager.get_icon('blue'),
                                        (35 + x_offset, 335 + y_offset - 5),
                                        img_manager.get_icon('blue'))
                            x_offset += 25
                        elif '{r}' in subsub_line.lower():
                            image.paste(img_manager.get_icon('red'),
                                        (35 + x_offset, 335 + y_offset - 5),
                                        img_manager.get_icon('blue'))
                            x_offset += 25
                        elif '{g}' in subsub_line.lower():
                            image.paste(img_manager.get_icon('green'),
                                        (35 + x_offset, 335 + y_offset - 5),
                                        img_manager.get_icon('blue'))
                            x_offset += 25
                        elif '{t}' in subsub_line.lower():
                            image.paste(img_manager.get_icon('tap'),
                                        (35 + x_offset, 335 + y_offset - 5),
                                        img_manager.get_icon('tap'))
                            x_offset += 25
                        else:
                            try:
                                int(subsub_line[1])
                                colorless_mana = img_manager.get_icon('colorless')
                                draw_colorless = ImageDraw.Draw(colorless_mana)
                                draw_colorless.text((8, 4),
                                                    str(subsub_line[1]),
                                                    fill=(0, 0, 0, 255),
                                                    font=font)

                                image.paste(colorless_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        colorless_mana)
                                colorless_mana.close()
                                x_offset += 25
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
    if card.types[0].lower() == 'creature':
        power = str(card.pt_p.count('^'))
        toughness = str(card.pt_t.count('^'))
        pt_image = Image.open('app/card_parts/magic-new.mse-style/' +
                              color[0] +
                              'pt.jpg')
        image.paste(pt_image, (271, 461))
        draw.text((295, 470), power + " / " + toughness, fill=(0, 0, 0, 255),
                  font=font)

    # Card image
    terms = magic_image.find_search_terms(card.encode())
    print("Search terms:", terms)
    for term in terms:
        #color = term[-1]
        query = "+".join(term[:-1])
        if color == 'u':
            color = 'blue'
        img_url = magic_image.fetch(query + '+"fantasy"+paintings+-card', color)
        if img_url:
            break
    with BytesIO(requests.get(img_url).content) as reader:
        reader.seek(0)
        art = Image.open(reader)
        art.thumbnail((311, 311))
        art = art.crop((0, 0, 311, 228))
        image.paste(art, (32, 62))

    return image