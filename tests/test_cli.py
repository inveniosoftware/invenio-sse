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


"""Test example app."""

import json
from time import sleep

import mock
from click.testing import CliRunner

from invenio_sse import cli, current_sse


def test_publish(app, script_info):
    """Test the format_sse_event."""
    channel = 'testchannel'
    runner = CliRunner()

    # mock pubsub to be able to subscribe before publish
    # and then mock subscribe to know if the application really subscribe to
    # the right channel
    pubsub = current_sse._pubsub()
    pubsub.subscribe(channel)
    pubsub.subscribe = mock.Mock()
    with mock.patch('invenio_sse.current_sse._pubsub', return_value=pubsub), \
            app.test_request_context():

        with runner.isolated_filesystem():
            with open('message.json', 'wb') as f:
                f.write(json.dumps(
                    {'hello': 'World'}, ensure_ascii=False
                ).encode('utf-8'))

            # send message
            res = runner.invoke(cli.sse, [
                'publish',
                'message.json',
                '--channel', channel,
                '--type', 'edit'
            ], obj=script_info)
            assert res.exit_code == 0

        # get the message formatted
        sleep(1)
        message = next(current_sse.messages(channel=channel))
        # check you are receiving the message sent
        assert message.startswith(
            'event:edit\ndata: ["{\\"hello\\": \\"World\\"}"]\nid:')
        assert message.endswith('\n\n')

        # and subscribe to the right channel
        (((subscribed, ), _), ) = pubsub.subscribe.call_args_list
        assert subscribed == channel
