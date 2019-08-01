# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

r"""Minimal Flask application example for development.

Install the redis-server.

Run example development server:

.. code-block:: console

   $ cd examples
   $ export FLASK_APP=app.py
   $ export FLASK_DEBUG=1
   $ flask run

Open the browser:

.. code-block:: console

   $ open http://0.0.0.0:5000/

Send a message through the console:

.. code-block:: console

   $ echo 'User X started to edit the project' |\
        flask sse publish project-1 edit

"""

from __future__ import absolute_import, print_function

from flask import Blueprint, Flask, current_app, render_template, request

from invenio_sse import InvenioSSE
from invenio_sse.proxies import current_sse

# Create Flask application
app = Flask(__name__)
InvenioSSE(app)

blueprint = Blueprint(
    'invenio_sse',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route("/sse")
def sse():
    """Stream server-sent events.

    Use ``channel`` URL argument to stream events from a different channel
    than the default, ``sse``.
    """
    channel = request.args.get('channel', 'sse')

    return current_app.response_class(
        current_sse.messages(channel=channel),
        mimetype='text/event-stream',
    )

app.register_blueprint(blueprint)


@app.route('/')
def index():
    """Index."""
    return render_template('app/index.html')
