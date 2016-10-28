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

import threading
import time

import pkg_resources
import pytest
from flask import url_for
from flask_security import url_for_security
from mock import patch

from invenio_sse import current_sse
from invenio_sse.contrib.deposit import InvenioSSEDeposit


def test_deposit_extension(app_deposit, deposit_integration):
    assert 'deposit' in app_deposit.extensions['invenio-sse'].integrations

    with patch('pkg_resources.get_distribution') as get_dist:
        get_dist.side_effect = pkg_resources.DistributionNotFound
        with pytest.raises(RuntimeError):
            InvenioSSEDeposit(app_deposit)


def test_deposit_sse(app_deposit, db, deposit, users, deposit_integration):
    with app_deposit.test_request_context():
        with app_deposit.test_client() as client:
            # Login
            client.post(url_for_security('login'), data=dict(
                email=users[0].email,
                password='tester'
            ))

            channel = url_for('invenio_deposit_sse.depid_sse',
                              pid_value=deposit['_deposit']['id'])

            message = 'Hello World!'

            class Connect(threading.Thread):
                def run(self):
                    with app_deposit.app_context():
                        # Connect to SSE channel
                        resp = client.get(channel)
                        assert resp.status_code == 200
                        assert 'text/event-stream' in \
                               resp.headers['Content-Type']
                        # Check that published message arrived
                        assert message in resp.response.next()

            # Establish connection
            connect_thread = Connect()
            connect_thread.start()
            time.sleep(1)

            # Publish message
            current_sse.publish(data=message, channel=channel, type_='message')

            connect_thread.join()
