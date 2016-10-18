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


"""Module tests."""

from __future__ import absolute_import, print_function

import json
import subprocess
from time import sleep

from flask import Flask

from invenio_sse import InvenioSSE, current_sse


def test_version():
    """Test version import."""
    from invenio_sse import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioSSE(app)
    assert 'invenio-sse' in app.extensions

    app = Flask('testapp')
    ext = InvenioSSE()
    assert 'invenio-sse' not in app.extensions
    ext.init_app(app)
    assert 'invenio-sse' in app.extensions


def test_pubsub(app):
    """Test publish."""
    with app.test_request_context():
        current_sse._pubsub.subscribe('testchannel')

        # get subscribe message
        sleep(1)
        message = current_sse._pubsub.get_message()
        assert message['type'] == 'subscribe'

        # send message
        current_sse.publish(data='hello world', channel='testchannel')
        # get the message
        sleep(1)
        message = current_sse._pubsub.get_message()
        assert message['type'] == 'message'
        assert message['channel'].decode('utf-8') == 'testchannel'
        assert json.loads(message['data'].decode('utf-8')) == \
            {"retry": None, "data": "hello world", "event": None, "id": None}

        # send message
        current_sse.publish(data='hello world', channel='testchannel',
                            type_='mytype', retry=123, id_=456)
        # get the message
        sleep(1)
        message = current_sse._pubsub.get_message()
        assert message['type'] == 'message'
        assert message['channel'].decode('utf-8') == 'testchannel'
        assert json.loads(message['data'].decode('utf-8')) == \
            {"retry": 123, "data": "hello world", "event": "mytype", "id": 456}

        # send message
        current_sse.publish(data='hello2', channel='testchannel',
                            type_='mytype2', retry=456, id_=789)
        # get the message formatted
        sleep(1)
        message = next(current_sse.messages())
        assert message == \
            'event:mytype2\ndata: "hello2"\nid:789\nretry:456\n\n'
