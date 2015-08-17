#!/usr/bin/env python3
__author__ = 'croxis'
import os
import sys
from app import create_app, get_scocket
from flask.ext.script import Server, Manager, Shell
# Manually adding mtgencode to path because hardcast sixdrop is a jerk for not
# adding __init__.py!
sys.path.append('./mtgencode/lib')
sys.path.append('./mtgencode')

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
socketio = get_scocket()
manager = Manager(app)


def make_shell_context():
    return dict(app=app)

class Run(Server):
    def run():
        print("hoho")
        socketio.run(app,
                    host='127.0.0.1',
                    port=5000,
                    use_reloader=True)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("run", Run())

if __name__ == '__main__':
    manager.run()
