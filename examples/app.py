# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

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
