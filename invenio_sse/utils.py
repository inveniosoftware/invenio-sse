# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
