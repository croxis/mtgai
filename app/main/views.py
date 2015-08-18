__author__ = 'croxis'
from datetime import datetime
from io import BytesIO, StringIO
import json
import os
from queue import Queue, Empty
import subprocess
from threading import Thread
import urllib.parse
import zipfile

from flask import redirect, render_template, request, send_file, session, \
    url_for
import lib.cardlib as cardlib
import lib.utils as utils
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader

from . import main
from ..card_visual import create_card_img
from .. import app, socketio
from .forms import GenerateCardsForm, MoreOptionsForm, SubmitCardsForm, \
    get_checkpoints_options


@socketio.on('my event')  # Decorator to catch an event called "my event":
def test_message(message):  # test_message() is the event callback function.
    print("I got a message:", message)
    socketio.emit('my response',
         {'data': 'got it!'})  # Trigger a new event called "my response"
    # that can be caught by another callback later in the program.


@main.route('/')
def index():
    return redirect(url_for('.index_mtgai'))


@main.route('/mtgai', methods=['GET', 'POST'])
def index_mtgai():
    random_form = GenerateCardsForm()
    random_form.checkpoint.choices = get_checkpoints_options()
    form = SubmitCardsForm()
    if random_form.validate_on_submit():
        session['render_mode'] = random_form.render_mode.data
        session['checkpoint_path'] = random_form.checkpoint.data
        session['seed'] = random_form.seed.data
        session['primetext'] = random_form.primetext.data
        session['length'] = random_form.length.data
        session['temperature'] = float(random_form.temperature.data)
        session['name'] = random_form.name.data
        session['supertypes'] = random_form.supertypes.data
        session['types'] = random_form.types.data
        session['subtypes'] = random_form.subtypes.data
        session['rarity'] = random_form.rarity.data
        session['bodytext_prepend'] = random_form.bodytext_prepend.data
        session['bodytext_append'] = random_form.bodytext_append.data
        return redirect(url_for('.card_select'))
    if form.validate_on_submit():
        session['cardtext'] = form.body.data
        session['cardsep'] = '\r\n\r\n'
        session['mode'] = "existing"
        session['render_mode'] = form.render_mode.data
        return redirect(url_for('.card_select'))
    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form,
                           random_form=random_form,
                           name='name',
                           title='MTG Automatic Inventor (MTGAI)')


@socketio.on('generate')
def card_generate():
    checkpoint_option = session['checkpoint_path']
    do_nn = checkpoint_option != "None"
    if do_nn:
        checkpoint_path = os.path.join(
            os.path.expanduser(app.config['SNAPSHOTS_PATH']),
            checkpoint_option)
    length = int(session['length'])
    if length > app.config['LENGTH_LIMIT']:
        length = app.config['LENGTH_LIMIT']
    socketio.emit('set max char', {'data': length})
    length += 140  # Small fudge factor to be a little more accurate with
                   # the amount of text actually generated
    use_render_mode(session["render_mode"])
    if do_nn:
        command = ['th', 'sample_hs_v3.1.lua', checkpoint_path, '-gpuid',
                   str(app.config['GPU'])]
    else:
        command = ['-gpuid', str(app.config['GPU'])]
    if session['seed']:
        command += ['-seed', str(session['seed'])]
    if session['primetext']:
        command += ['-primetext', session['primetext']]
    if session['length']:
        command += ['-length', str(length)]
    if session['temperature']:
        command += ['-temperature', str(session['temperature'])]
    if session['name']:
        command += ['-name', session['name']]
    if session['types']:
        command += ['-types', session['types']]
    if session['supertypes']:
        command += ['-supertypes', session['supertypes']]
    if session['subtypes']:
        command += ['-subtypes', session['subtypes']]
    if session['rarity']:
        command += ['-rarity', session['rarity']]
    if session['bodytext_prepend']:
        command += ['-bodytext_prepend', session['bodytext_prepend']]
    if session['bodytext_append']:
        command += ['-bodytext_append', session['bodytext_append']]
    if do_nn:
        session['mode'] = "nn"
        output = ''
        with subprocess.Popen(command,
                              cwd=os.path.expanduser(
                                  app.config['GENERATOR_PATH']),
                              shell=False,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True) as process:
            while process.poll() is None:
                print("Debug timing statement to investigate server stall 1")
                line = process.stdout.readline()
                print("Debug timing statement to investigate server stall 2")
                if line.startswith('|') and line.endswith('|\n'):
                    socketio.emit('raw card', {'data': line})
                    if session["do_text"]:
                        card = convert_to_card(line)
                        if card:
                            socketio.emit('text card', {'data': card.format().replace('@', card.name.title()).split('\n')})
                    if session["do_images"]:
                        socketio.emit('image card', {'data': urllib.parse.quote(line, safe='') + session[
                    "image_extra_params"]})
                    output += line + '\n'  # Recreate the output from the sampler
                print("Debug timing statement to investigate server stall 3")
        session['cardtext'] = output
        session['cardsep'] = '\n\n'
    else:
        session['mode'] = "dummy"
        session['command'] = " ".join(command)
    socketio.emit('finished generation', {'data': ''})


@main.route('/mtgai/card-select', methods=['GET', 'POST'])
def card_select():
    checkpoint_option = session['checkpoint_path']
    do_nn = checkpoint_option != "None"
    if do_nn:
        session['mode'] = "nn"
    else:
        session['mode'] = "dummy"
        session['command'] = "This needs some fixing and reorganization"
    if session['mode'] == "dummy":
        return render_template('nn_dummy.html', command=session['command'])
    else:
        use_render_mode(session["render_mode"])
        extra_template_data = {}
        extra_template_data['form'] = MoreOptionsForm(
            can_print=session["can_print"], can_mse_set=session["can_mse_set"])
        if session["can_print"]:
            if extra_template_data['form'].validate_on_submit():
                if extra_template_data['form'].print_button.data:
                    return redirect(url_for('.print_cards'))
        if session["can_mse_set"]:
            if extra_template_data['form'].validate_on_submit():
                if extra_template_data['form'].mse_set_button.data:
                    return redirect(url_for('.download_mse_set'))
        return render_template(session["render_template"],
                               **extra_template_data)


def use_render_mode(render_mode):
    session["do_images"] = False
    session["do_text"] = False
    session["can_print"] = False
    session["can_mse_set"] = True
    if render_mode == "image":
        session["do_images"] = True
        session["do_google"] = True
        session["can_print"] = True
        session["image_extra_params"] = ""
        session["render_template"] = 'card_select_image.html'
    elif render_mode == "image_searchless":
        session["do_images"] = True
        session["do_google"] = False
        session["can_print"] = True
        session["image_extra_params"] = "?no-google=True"
        session["render_template"] = 'card_select_image_no_google.html'
    elif render_mode == "text":
        session["do_text"] = True
        session["render_template"] = 'card_select_text.html'
    else:
        session["render_template"] = 'card_select_raw_only.html'


@main.route('/mtgai/download-mse-set', methods=['GET', 'POST'])
def download_mse_set():
    set_text = b''
    cards = convert_to_cards(session['cardtext'])
    zipped_bytes = BytesIO()
    set_text += (utils.mse_prepend.encode())
    for card in cards:
        set_text += card.to_mse().encode('utf-8')
        set_text += b'\n'
    set_text += b'version control:\n\ttype: none\napprentice code: '
    zipped = zipfile.ZipFile(zipped_bytes, mode='w')
    zipped.writestr('set', set_text)
    zipped.close()
    zipped_bytes.seek(0)
    return send_file(zipped_bytes, mimetype='application/zip',
                     as_attachment=True, attachment_filename="nn-set.mse-set")


@main.route('/mtgai/print', methods=['GET', 'POST'])
def print_cards():
    # LETTER = (8.5, 11)
    LETTER = (11, 8.5)
    DPI = 72
    # Set print margins
    MARGIN = 0.5
    x_offset = int(MARGIN * DPI)
    y_offset = int(MARGIN * DPI)
    CARDSIZE = (int(2.49 * DPI), int(3.48 * DPI))
    # scale = CARDSIZE[0] / 375.0  # Default cardsize in px
    cards = convert_to_cards(session['cardtext'])
    byte_io = BytesIO()
    from reportlab.pdfgen import canvas
    canvas = canvas.Canvas(byte_io, pagesize=landscape(letter))
    WIDTH, HEIGHT = landscape(letter)
    # draw = ImageDraw.Draw(sheet)
    for card in cards:
        image = create_card_img(card, session["do_google"])
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
                urls.append(urllib.parse.quote(card_src, safe='') + session[
                    "image_extra_params"])

    return urls


def convert_to_card(card_src):
    """Convert a single line of text to a Card. Returns none if invalid."""
    card = cardlib.Card(card_src)
    if card.valid:
        return card


def convert_to_cards(text, cardsep='\r\n\r\n'):
    """Card separation is \r\n\r\n when submitted by form and \n\n by text
    file."""
    cards = []
    for card_src in text.split(cardsep):
        card = convert_to_card(card_src)
        if card:
            cards.append(card)
    return cards


def convert_to_text(text, cardsep='\r\n\r\n'):
    cards = convert_to_cards(text, cardsep)
    text = []
    for card in cards:
        text.extend(card.format().replace('@', card.name.title()).split('\n'))
        text.append("------------------------")
    return text[:-1]
