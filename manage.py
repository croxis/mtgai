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
    def __call__(self, app, host, port, use_debugger, use_reloader,
                 threaded, processes, passthrough_errors):
        # we don't need to run the server in request context
        # so just run it directly

        if use_debugger is None:
            use_debugger = app.debug
            if use_debugger is None:
                use_debugger = True
                if sys.stderr.isatty():
                    print(
                        "Debugging is on. DANGER: Do not allow random users to connect to this server.",
                        file=sys.stderr)
        if use_reloader is None:
            use_reloader = app.debug
        socketio.run(host=host,
                     port=port,
                     use_reloader=use_reloader,
                     **self.server_options)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("run", Run())

if __name__ == '__main__':
    manager.run()
