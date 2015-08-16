import random
import glob
import os.path

from flask_wtf import Form
from wtforms import DecimalField, IntegerField, SelectField, SubmitField
from wtforms import TextField
from wtforms import TextAreaField
from wtforms.validators import NumberRange, Required

from .. import app

__author__ = 'croxis'


def get_checkpoints():
    checkpoints = {}
    brain_path = os.path.expanduser(app.config['SNAPSHOTS_PATH'])
    brain_path = os.path.join(brain_path, '*')
    brain_directories = glob.glob(brain_path)
    for directory in brain_directories:
        brain_name = os.path.split(directory)[-1]
        for checkpoint in glob.glob(os.path.join(directory, '*.t7')):
            if brain_name not in checkpoints:
                checkpoints[brain_name] = []
            path, item = os.path.split(checkpoint)
            epoch, loss = item.lstrip('lm_lstm_epoch').rstrip('.t7').split('_')
            checkpoints[brain_name].append({'path': path,
                                            'epoch': epoch,
                                            'loss': loss})
    return checkpoints


def get_checkpoints_simple():
    checkpoints = []
    brain_path = os.path.expanduser(app.config['SNAPSHOTS_PATH'])
    brain_path = os.path.join(brain_path, '*')
    brain_directories = glob.glob(brain_path)
    for directory in brain_directories:
        brain_name = os.path.split(directory)[-1]
        for checkpoint in sorted(glob.glob(os.path.join(directory, '*.t7')),
                                 reverse=True):
            path, item = os.path.split(checkpoint)
            epoch, loss = item.lstrip('lm_lstm_epoch').rstrip('.t7').split('_')
            checkpoints.append({'brain_name': brain_name,
                                'path': checkpoint,
                                'epoch': epoch,
                                'loss': loss,
                                'file': item})
    return checkpoints


class GenerateCardsForm(Form):
    submit = SubmitField("Generate")
    '''brain = SelectField(label="Brain",
                        choices=[(b, b) for b in get_checkpoints().keys()])
    checkpoint = SelectField(label="Checkpoint",
                             choices=[(c['epoch'], c['epoch']) for c in get_checkpoints()[b] for b in get_checkpoints().keys()])'''
    '''checkpoint = SelectField(label="Checkpoint",
                             choices=[(b['path'],
                                       b['brain_name'] + ' epoch: ' + b[
                                           'epoch']) for b in
                                      get_checkpoints_simple()])'''
    checkpoint = SelectField(label="Checkpoint",
                             choices=[
                                 (os.path.join(b['brain_name'], b['file']),
                                  b['brain_name'] + ' epoch: ' + b[
                                      'epoch'] + ' loss: ' + b['loss']) for b
                                 in get_checkpoints_simple()],
                             description='Higher epoch and lower loss is a smarter brain.')
    seed = IntegerField(label="Random seed", default=random.randint(0, 255))
    # sample = boolean
    primetext = TextField(label="Suggest",
                          description='"Seed" the ai with suggested words')
    length = IntegerField(label="Length",
                          default=2000,
                          description="How many characters to generate. About 100 per card. Max is " + str(
                              app.config['LENGTH_LIMIT']),
                          validators=[NumberRange(min=0, max=app.config[
                              'LENGTH_LIMIT']),
                                      Required()])
    temperature = DecimalField(label="Temperature",
                               default=0.7,
                               description="0.0 -- 1.0 How adventurous the generator is. High number results in more creativity.",
                               validators=[NumberRange(min=0, max=200),
                                           Required()])
    name = TextField(label="Name",
                     description='Add to the start of all card names. EX: Goblin')
    supertypes = TextField(label="Super Types",
                           description='Add to the start of all card super types. EX: Elite')
    types = TextField(label="Types",
                      description='Add to the start of all card types. EX: Enchantment')
    # Loyalty
    subtypes = TextField(label="Subtypes",
                         description='Add to the start of all card subtypes. EX: Bear')
    rarity = TextField(label="Rarity", description='Card rarity.')
    bodytext_prepend = TextField(label="Prepend body text",
                                 description='Added to the start of the text section.')
    bodytext_append = TextField(label="Append body text",
                                description='Added to the end of the text section.')


class SubmitCardsForm(Form):
    body = TextAreaField("Copy and paste card data here.",
                         validators=[Required()])
    submit = SubmitField("Submit")


class PrintCardsForm(Form):
    submit = SubmitField("Print")
