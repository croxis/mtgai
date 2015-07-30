__author__ = 'croxis'
from io import BytesIO, StringIO
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont
import requests

import lib.transforms as transforms
import lib.utils as utils
from lib.manalib import Manatext

from . import magic_image

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

    # image = Image.open("app/card_parts/magic-new.mse-style/acard.jpg")
    if color == 'blue':
        color = 'u'
    image = Image.open("app/card_parts/magic-new.mse-style/" +
                       color[0] +
                       "card.jpg")
    font = ImageFont.truetype("fonts/matrixb.ttf", size=20)
    draw = ImageDraw.Draw(image)

    # Card costs
    red_mana = Image.open(
        'app/card_parts/magic-mana-beveled.mse-symbol-font/mana_r.png')
    green_mana = Image.open(
        'app/card_parts/magic-mana-beveled.mse-symbol-font/mana_g.png')
    black_mana = Image.open(
        'app/card_parts/magic-mana-beveled.mse-symbol-font/mana_b.png')
    blue_mana = Image.open(
        'app/card_parts/magic-mana-beveled.mse-symbol-font/mana_u.png')
    white_mana = Image.open(
        'app/card_parts/magic-mana-beveled.mse-symbol-font/mana_w.png')
    colorless_mana = Image.open(
        'app/card_parts/magic-mana-beveled.mse-symbol-font/mana_circle.png')
    tap = Image.open(
        'app/card_parts/magic-mana-beveled.mse-symbol-font/mana_t.png')
    red_mana.thumbnail((25, 25))
    green_mana.thumbnail((25, 25))
    black_mana.thumbnail((25, 25))
    blue_mana.thumbnail((25, 25))
    white_mana.thumbnail((25, 25))
    colorless_mana.thumbnail((25, 25))
    tap.thumbnail((25, 25))

    y_offset = 0
    for x in range(0, cost['white']):
        image.paste(white_mana, (320 - y_offset, 29), white_mana)
        y_offset += 25
    for x in range(0, cost['blue']):
        image.paste(blue_mana, (320 - y_offset, 29), white_mana)
        y_offset += 25
    for x in range(0, cost['black']):
        image.paste(black_mana, (320 - y_offset, 29), white_mana)
        y_offset += 25
    for x in range(0, cost['green']):
        image.paste(green_mana, (320 - y_offset, 29), white_mana)
        y_offset += 25
    for x in range(0, cost['red']):
        image.paste(red_mana, (320 - y_offset, 29), white_mana)
        y_offset += 25
    if cost['colorless']:
        colorless_mana_copy = colorless_mana.copy()
        draw_colorless = ImageDraw.Draw(colorless_mana_copy)
        draw_colorless.text((8, 4),
                            str(cost['colorless']),
                            fill=(0, 0, 0, 255),
                            font=font)
        image.paste(colorless_mana_copy,
                    (320 - y_offset, 29),
                    colorless_mana_copy)

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
                            image.paste(white_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        elif '{b}' in subsub_line.lower():
                            image.paste(black_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        elif '{u}' in subsub_line.lower():
                            image.paste(blue_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        elif '{r}' in subsub_line.lower():
                            image.paste(red_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        elif '{g}' in subsub_line.lower():
                            image.paste(green_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        elif '{b}' in subsub_line.lower():
                            image.paste(black_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        elif '{t}' in subsub_line.lower():
                            image.paste(tap,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        tap)
                            x_offset += 25
                        else:
                            try:
                                int(subsub_line[1])
                                colorless_mana_copy = colorless_mana.copy()
                                draw_colorless = ImageDraw.Draw(colorless_mana_copy)
                                draw_colorless.text((8, 4),
                                                    str(subsub_line[1]),
                                                    fill=(0, 0, 0, 255),
                                                    font=font)

                                image.paste(colorless_mana_copy,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        colorless_mana_copy)
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
    for term in terms:
        #color = term[-1]
        query = "+".join(term[:-1])
        if color == 'u':
            color = 'blue'
        img_url = magic_image.fetch(query + '+"fantasy"+paintings+-card', color)
        if img_url:
            break
    with BytesIO(requests.get(img_url).content) as reader:
        #mask = Image.open("app/card_parts/magic-new.mse-style/imagemask_standard.png")
        reader.seek(0)
        art = Image.open(reader)
        #art.thumbnail((311, 228))
        art.thumbnail((311, 311))
        art = art.crop((0, 0, 311, 228))
        image.paste(art, (32, 62))

    return image