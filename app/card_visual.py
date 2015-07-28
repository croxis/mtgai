__author__ = 'croxis'
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

import lib.transforms as transforms


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
    red_mana.thumbnail((25, 25))
    green_mana.thumbnail((25, 25))
    black_mana.thumbnail((25, 25))
    blue_mana.thumbnail((25, 25))
    white_mana.thumbnail((25, 25))
    colorless_mana.thumbnail((25, 25))

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
        draw_colorless = ImageDraw.Draw(colorless_mana)
        draw_colorless.text((8, 4),
                            str(cost['colorless']),
                            fill=(0, 0, 0, 255),
                            font=font)
        image.paste(colorless_mana, (320 - y_offset, 29), colorless_mana)

    # Card texts
    draw.text((35, 35),
              # card.name.format(gatherer=True),
              card.name.title(),
              fill=(0, 0, 0, 255),
              font=font)
    draw.text((35, 300), card.types[0].title(), fill=(0, 0, 0, 255), font=font)
    # card_text = card.text.format()
    mtext = card.text
    mtext = transforms.text_unpass_1_choice(mtext, delimit=True)
    mtext = transforms.text_unpass_2_counters(mtext)
    mtext = transforms.text_unpass_3_unary(mtext)
    # We will do step 4 and 6 ourselves due to Manatext not having replace()
    # mtext = transforms.text_unpass_4_cardname(mtext, card.name)
    mtext = transforms.text_unpass_5_symbols(mtext, for_forum=False)
    # mtext = transforms.text_unpass_6_newlines(mtext)
    card_text = mtext.format()
    card_text = card_text.capitalize() # Before we inset title to preserve title caps
    card_text = card_text.replace('@', card.name.title())
    card_text = card_text.replace('\\', '\n')
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
                        if '{b}' in subsub_line.lower():
                            image.paste(black_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        if '{u}' in subsub_line.lower():
                            image.paste(blue_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        if '{r}' in subsub_line.lower():
                            image.paste(red_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        if '{g}' in subsub_line.lower():
                            image.paste(green_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
                        if '{b}' in subsub_line.lower():
                            image.paste(black_mana,
                                        (35 + x_offset, 335 + y_offset - 5),
                                        black_mana)
                            x_offset += 25
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
    return image