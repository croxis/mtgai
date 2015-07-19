__author__ = 'croxis'
from datetime import datetime
from flask import redirect, render_template, session, url_for

from . import main
from .forms import SubmitCardsForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = SubmitCardsForm()
    if form.validate_on_submit():
        # things
        return redirect(url_for('.index'))
    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form,
                           name='name',
                           title='MTG Automatic Inventor (MTGAI)')
