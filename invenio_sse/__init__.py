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

r"""Invenio module for HTML5 server-sent events support.

The main goal of this module is to provide a channel of communication between
the server and the client user the Server-sent event (SSE) protocol.

Initialization
--------------
First create a Flask application:

>>> from flask import Flask
>>> app = Flask('myapp')
>>> app.config['SSE_REDIS_URL'] = 'redis://localhost:6379/0'

You initialize Invenio SSE like a normal Flask extension:

>>> from invenio_sse import InvenioSSE
>>> ext_sse = InvenioSSE(app)
>>> from flask import Blueprint, Flask, current_app, render_template, request
>>> blueprint = Blueprint(
...    'invenio_sse',
...    'invenio_sse',
... )
>>> @blueprint.route("/sse")
... def sse():
...     channel = request.args.get('channel', 'sse')
...     return current_app.response_class(
...         current_sse.messages(channel=channel),
...         mimetype='text/event-stream',
...     )
>>> app.register_blueprint(blueprint)

In order for the following examples to work, you need to work within an
Flask application context so let's push one:

>>> ctx = app.app_context()
>>> ctx.push()

Also, for the examples to work you need Redis running.

Publish messages
----------------
This should put a message in Redis in the general channel with no additional
information:

>>> from invenio_sse import current_sse
>>> current_sse.publish({'code':'COOL', 'msg':'cool message'})

Now we can subscribe to receive the messages:

>>> with app.test_client() as client:
...    res = client.get('/sse')
>>> res.status_code
200
>>> res.mimetype
'text/event-stream'

There is also the possibility to specify the type of the event, the id, the
retry time in case the connection gets lost and also if you want the particular
channel to publish the message:

>>> current_sse.publish(
...    {'code':'ACK', 'msg':'cool message'},
...    type_='cool',
...    id_=12345,
...    retry=6000,
...    channel='cool_channel'
... )
>>> with app.test_client() as client:
...   res = client.get('/sse?channel=cool_channel')
>>> res.status_code
200

Publishing messages from the command line:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can also publish messages using the CLI that this package provides (we will
use the example app):

.. code-block:: console

    $ cd examples
    $ export FLASK_APP=app.py
    $ echo '{"code": "ACK", "msg": "cool message"}' | \
      flask sse publish --channel cool_channel

To see more about the CLI ``flask sse publish --help``.

Receiving messages
------------------
Receiving messages in the web browser is rather simple, this is an example of
the javascript code that you could use to subscribe to messages like the ones
we send in the examples above:

.. code-block:: javascript

    window.onload = function setDataSource() {
      if (!!window.EventSource) {
        var source = new EventSource(
            "http://0.0.0.0:5000/sse?channel=cool_channel");

        source.onmessage = function(msg) {
          console.log(msg);
        };
        source.addEventListener('cool', function(msg){
          var li = document.createElement('li');
          var type = msg.type;
          var data = msg.data;
          li.appendChild(
              document.createTextNode("type: "+type+" data: "+data));
          document.getElementById('messages').appendChild(li);
        });

      } else {
        document.getElementById("notSupported").style.display = "block";
      }
    }


You can find a complete example on how to use Invenio-SSE in the examples
folder.
"""

from __future__ import absolute_import, print_function

from .ext import InvenioSSE
from .proxies import current_sse
from .version import __version__

__all__ = ('__version__', 'InvenioSSE', 'current_sse')
