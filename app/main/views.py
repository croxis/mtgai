__author__ = 'croxis'
from datetime import datetime
from io import BytesIO
import urllib.parse

from flask import redirect, render_template, send_file, session, url_for
import lib.cardlib as cardlib
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from . import main
from .. import magic_image
from ..card_visual import create_card_img
from .forms import PrintCardsForm, SubmitCardsForm


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
    urls = convert_to_urls(session['card text'])
    form = PrintCardsForm()
    if form.validate_on_submit():
        return redirect(url_for('.print_cards'))
    return render_template('card_select.html', form=form, urls=urls)


@main.route('/mtgai/print', methods=['GET', 'POST'])
def print_cards():
    #LETTER = (8.5, 11)
    LETTER = (11, 8.5)
    DPI = 100
    # Set print margins
    MARGIN = 0.5
    x_offset = int(MARGIN * DPI)
    y_offset = int(MARGIN * DPI)
    CARDSIZE = (int(2.49 * DPI), int(3.48 * DPI))
    #scale = CARDSIZE[0] / 375.0  # Default cardsize in px
    cards = convert_to_cards(session['card text'])
    sheets = [Image.new('RGB',
                        tuple(int(DPI * x) for x in LETTER),
                        color=(255, 255, 255))]
    #canvas = canvas.Canvas("cards.pdf", pagesize=letter)
    #draw = ImageDraw.Draw(sheet)
    for card in cards:
        image = create_card_img(card)
        image.thumbnail(CARDSIZE)
        sheets[-1].paste(image, (x_offset, y_offset))
        x_offset += CARDSIZE[0] + 5  # 5 px border around cards
        if x_offset + CARDSIZE[0] > LETTER[0] * DPI:
            x_offset = int(MARGIN * DPI)
            y_offset += CARDSIZE[1] + 5
        if y_offset + CARDSIZE[1] > LETTER[1] * DPI:
            x_offset = int(MARGIN * DPI)
            y_offset = int(MARGIN * DPI)
            sheets.append(Image.new('RGB',
                                    tuple(int(DPI * x) for x in LETTER),
                                    color=(255, 255, 255)))
    byte_io = BytesIO()
    #sheets[0].save(byte_io, 'PDF')
    sheets[0].save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')
    #return send_file(byte_io, mimetype='application/pdf')


def convert_to_urls(card_text, cardsep='\r\n\r\n'):
    urls = []
    for card_src in card_text.split(cardsep):
        if card_src:
            card = cardlib.Card(card_src)
            if card.valid:
                urls.append(urllib.parse.quote(card_src, safe=''))

    return urls


def convert_to_cards(text, cardsep='\r\n\r\n'):
    """Card separation is \r\n\r\n when submitted by form and \n\n by text
    file."""
    cards = []
    for card_src in text.split(cardsep):
        if card_src:
            card = cardlib.Card(card_src)
            if card.valid:
                cards.append(card)
    return cards
