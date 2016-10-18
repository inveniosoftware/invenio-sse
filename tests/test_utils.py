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

import pytest

from invenio_sse.utils import format_sse_event


def test_format_sse_json():
    """Test the format_sse_event."""
    # field 'data' is mandatory
    with pytest.raises(AssertionError):
        format_sse_event({
            'id': 1, 'event': 'test', 'retry': 100,
        })

    # simplest message
    assert 'data: "hello"\n\n' == format_sse_event({'data': 'hello'})

    # multilines message
    message = format_sse_event({'data': 'hello\nworld'})
    assert 'data: "hello\\nworld"\n\n' == message

    # json message
    message = format_sse_event({
        'data': {
            'a': 'hello',
            'b': 'world',
        }
    })
    assert message in ('data: {"a": "hello", "b": "world"}\n\n',
                       'data: {"b": "world", "a": "hello"}\n\n')

    # text with EOM (End Of Message)
    message = format_sse_event({
        'data': 'end of\n\nmessage',
    })
    assert message == 'data: "end of\\n\\nmessage"\n\n'

    # complete message
    message = format_sse_event({
        'event': 'hello',
        'data': 'end of\n\nmessage',
        'retry': '123'
    })
    assert message == 'event:hello\ndata: "end of\\n\\nmessage"\nretry:123\n\n'
