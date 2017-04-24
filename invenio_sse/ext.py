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

"""Invenio module for HTML5 server-sent events support."""

from __future__ import absolute_import, print_function

import json
import time

import pkg_resources
from redis import StrictRedis

from . import config
from .utils import format_sse_event


class _SSEState(object):
    """SSE state accessible via ``proxies.current_sse``."""

    def __init__(self, app, entry_point_group=None):
        """Initialize state."""
        self.app = app
        self._redis = StrictRedis.from_url(app.config['SSE_REDIS_URL'])
        self.integrations = {}

        if entry_point_group:
            self.load_integration(entry_point_group)

    def register_integration(self, integration_id, integration):
        """Register an SSE integration with another module."""
        self.integrations[integration_id] = integration(self.app)

    def load_integration(self, entry_point_group):
        """Load integration from an entry point group."""
        for ep in pkg_resources.iter_entry_points(entry_point_group):
            self.register_integration(ep.name, ep.load())

    def publish(self, data, type_=None, id_=None, retry=None, channel='sse'):
        """Publish data as a server-sent event.

        :param data: Event data, any object serialize to JSON.
        :param type_: Optional type of the event.
        :param id_: Optional event ID to set the EventSource object's last
                    event ID value.
        :param retry: Optional reconnection time to use when attempting to send
                      the event.
        :param channel: Optional channel to direct events to different clients,
                        by defaul ``sse``.
        """
        id_ = id_ or time.time()
        msg = {"data": data, "event": type_, "id": id_, "retry": retry}
        self._redis.publish(channel, json.dumps(msg))

    def _pubsub(self):
        """A redis pubsub instance."""
        return self._redis.pubsub()

    def messages(self, channel='sse'):
        """Message generator from the given channel."""
        pubsub = self._pubsub()
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            if message['type'] == 'message':
                yield format_sse_event(
                    json.loads(message['data'].decode('utf-8')))


class InvenioSSE(object):
    """Invenio-SSE extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, entry_point_group='invenio_sse.integrations'):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-sse'] = _SSEState(app, entry_point_group)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('SSE_'):
                app.config.setdefault(k, getattr(config, k))
