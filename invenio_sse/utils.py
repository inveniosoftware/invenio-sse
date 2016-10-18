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

"""Utils."""

from __future__ import absolute_import, print_function

import json


def format_sse_event(event):
    r"""Encode a new event following SSE standard.

    .. code-block:: text

        event: "New message"\n
        id: 12345\n
        data: {\n
        data: "msg": "hello world",\n
        data: }\n
        retry: 10000\n\n

    :param event: A dictionary containing the keys ``data``, ``id``, ``retry``
                  and ``event``. Only ``data`` field is mandatory, all the
                  other fields are optional.
    :returns: A formatted SSE message.
    """
    assert 'data' in event

    lines = [
        'data: {0}'.format(line)
        for line in json.dumps(event['data']).splitlines()
    ]

    if event.get('event'):
        lines.insert(0, 'event:{event}'.format(**event))
    if event.get('id'):
        lines.append('id:{id}'.format(**event))
    if event.get('retry'):
        lines.append('retry:{retry}'.format(**event))

    return '\n'.join(lines) + '\n\n'
