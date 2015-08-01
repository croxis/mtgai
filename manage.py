#!/usr/bin/env python3
__author__ = 'croxis'
import os
import sys
from app import create_app
from flask.ext.script import Manager, Shell
# Manually adding mtgencode to path because hardcast sixdrop is a jerk for not
# adding __init__.py!
sys.path.append('./mtgencode/lib')
sys.path.append('./mtgencode')

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app)

manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
