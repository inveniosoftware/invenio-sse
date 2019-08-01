# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


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

                def __init__(self):
                    super(Connect, self).__init__()
                    self._return = None

                def join(self, timeout=None):
                    super(Connect, self).join(timeout)
                    return self._return

                def run(self):
                    with app_deposit.app_context():
                        # Connect to SSE channel
                        resp = client.get(channel)
                        self._return = (resp.status_code,
                                        resp.headers['Content-Type'],
                                        next(resp.response).decode('utf-8'))

            # Establish connection
            connect_thread = Connect()
            connect_thread.start()
            time.sleep(1)

            # Publish message
            current_sse.publish(data=message, channel=channel, type_='message')

            (status_code, content_type, msg) = connect_thread.join()
            assert status_code == 200
            assert 'text/event-stream' in content_type
            assert message in msg
