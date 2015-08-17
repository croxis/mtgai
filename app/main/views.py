__author__ = 'croxis'
from datetime import datetime
from io import BytesIO, StringIO
import json
import os
import subprocess
import urllib.parse

from flask import redirect, render_template, request, send_file, session, url_for
import lib.cardlib as cardlib
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from . import main
from ..card_visual import create_card_img
from .. import app
from .forms import GenerateCardsForm, PrintCardsForm, SubmitCardsForm, get_checkpoints_simple


@main.route('/')
def index():
    return redirect(url_for('.index_mtgai'))


@main.route('/mtgai', methods=['GET', 'POST'])
def index_mtgai():
    random_form = GenerateCardsForm()
    random_form.checkpoint.choices = [(os.path.join(b['brain_name'], b['file']),
                                       b['brain_name'] + ' epoch: ' + b[
                                           'epoch'] + ' loss: ' + b[
                                           'loss']) for b in
                                      get_checkpoints_simple()]
    form = SubmitCardsForm()
    if random_form.validate_on_submit():
        return redirect(url_for('.card_generate',
                                checkpoint_path=random_form.checkpoint.data,
                                seed=random_form.seed.data,
                                primetext=random_form.primetext.data,
                                length=random_form.length.data,
                                temperature=random_form.temperature.data,
                                name=random_form.name.data,
                                supertypes=random_form.supertypes.data,
                                types=random_form.types.data,
                                subtypes=random_form.subtypes.data,
                                rarity=random_form.rarity.data,
                                bodytext_prepend=random_form.bodytext_prepend.data,
                                bodytext_append=random_form.bodytext_append.data,
                                ))
    if form.validate_on_submit():
        session['cardtext'] = form.body.data
        session['cardsep'] = '\r\n\r\n'
        return redirect(url_for('.card_select'))
    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form,
                           random_form=random_form,
                           name='name',
                           title='MTG Automatic Inventor (MTGAI)')


@main.route('/mtgai/card-generate/')
def card_generate():
    checkpoint_path = os.path.join(os.path.expanduser(app.config['SNAPSHOTS_PATH']),
                                   request.args.get('checkpoint_path'))
    length = int(request.args.get('length'))
    if length > app.config['LENGTH_LIMIT']:
        length = app.config['LENGTH_LIMIT']
    command = ['th', 'sample_hs_v3.lua', checkpoint_path, '-gpuid', str(app.config['GPU'])]
    if request.args.get('seed'):
        command.append('-seed')
        command.append(request.args.get('seed'))
    if request.args.get('primetext'):
        command.append('-primetext')
        command.append(request.args.get('primetext'))
    if request.args.get('length'):
        command.append('-length')
        command.append(str(length))
    if request.args.get('temperature'):
        command.append('-temperature')
        command.append(str(request.args.get('temperature')))
    if request.args.get('name'):
        command += ['-name', request.args.get('name')]
    if request.args.get('types'):
        command += ['-types', request.args.get('types')]
    if request.args.get('supertypes'):
        command += ['-supertypes', request.args.get('supertypes')]
    if request.args.get('subtypes'):
        command += ['-subtypes', request.args.get('subtypes')]
    if request.args.get('rarity'):
        command += ['-rarity', request.args.get('rarity')]
    if request.args.get('bodytext_prepend'):
        command += ['-bodytext_prepend', request.args.get('bodytext_prepend')]
    if request.args.get('bodytext_append'):
        command += ['-bodytext_append', request.args.get('bodytext_append')]
    session['cardtext'] = subprocess.check_output(command,
                                     cwd=os.path.expanduser(app.config['GENERATOR_PATH']),
                                     shell=False,
                                     stderr=subprocess.STDOUT).decode()
    session['cardsep'] = '\n\n'
    return redirect(url_for('.card_select'))


@main.route('/mtgai/card-select', methods=['GET', 'POST'])
def card_select():
    urls = convert_to_urls(session['cardtext'], cardsep=session['cardsep'])
    form = PrintCardsForm()
    if form.validate_on_submit():
        return redirect(url_for('.print_cards'))
    return render_template('card_select.html', form=form, urls=urls)


@main.route('/mtgai/print', methods=['GET', 'POST'])
def print_cards():
    #LETTER = (8.5, 11)
    LETTER = (11, 8.5)
    DPI = 72
    # Set print margins
    MARGIN = 0.5
    x_offset = int(MARGIN * DPI)
    y_offset = int(MARGIN * DPI)
    CARDSIZE = (int(2.49 * DPI), int(3.48 * DPI))
    #scale = CARDSIZE[0] / 375.0  # Default cardsize in px
    cards = convert_to_cards(session['cardtext'])
    byte_io = BytesIO()
    from reportlab.pdfgen import canvas
    canvas = canvas.Canvas(byte_io, pagesize=landscape(letter))
    WIDTH, HEIGHT = landscape(letter)
    #draw = ImageDraw.Draw(sheet)
    for card in cards:
        image = create_card_img(card)
        image_reader = ImageReader(image)
        canvas.drawImage(image_reader,
                         x_offset,
                         y_offset,
                         width=CARDSIZE[0],
                         height=CARDSIZE[1])
        x_offset += CARDSIZE[0] + 5  # 5 px border around cards
        if x_offset + CARDSIZE[0] > LETTER[0] * DPI:
            x_offset = int(MARGIN * DPI)
            y_offset += CARDSIZE[1] + 5
        if y_offset + CARDSIZE[1] > LETTER[1] * DPI:
            x_offset = int(MARGIN * DPI)
            y_offset = int(MARGIN * DPI)
            canvas.showPage()
    canvas.save()
    byte_io.seek(0)
    return send_file(byte_io, mimetype='application/pdf')


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
