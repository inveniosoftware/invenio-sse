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

"""Command Line Interface."""

from __future__ import absolute_import, print_function

import sys

import click
from flask.cli import with_appcontext

from . import current_sse


@click.group()
def sse():
    """SSE commands."""


@sse.command('publish')
@click.argument('data', type=click.File('r'), default=sys.stdin)
@click.option('--type', 'type_',
              help='The event\'s type.  If this is specified, an event will be'
              ' dispatched on the browser to the listener for the specified'
              ' event name. The onmessage handler is called if no event name'
              ' is specified for a message')
@click.option('--id', 'id_',
              help='The event ID to set the EventSource object\'s last event'
              ' ID value.')
@click.option('--retry',
              help='The reconnection time to use when attempting to send the'
              ' event (miliseconds)')
@click.option('--channel',
              help='Channel to direct events to different clients, by default '
              'sse')
@with_appcontext
def publish(data, type_=None, id_=None, retry=None, channel='sse'):
    """Publish a message."""
    current_sse.publish(
        data=data.readlines(),
        type_=type_,
        id_=id_,
        retry=retry,
        channel=channel)


@sse.command('subscribe')
@click.option('--channel',
              help='Channel to direct events to different clients, by default '
              'sse')
@with_appcontext
def subscribe(channel='sse'):
    """Subscribe a channel."""
    for message in current_sse.messages(channel=channel):
        print(message)
