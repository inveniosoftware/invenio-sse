# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


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
