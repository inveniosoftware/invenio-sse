# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration of the SSE module."""

from __future__ import absolute_import, print_function

SSE_REDIS_URL = 'redis://localhost:6379/0'
"""Redis URL used to push and read the messages.

It should be in the form ``redis://username:password@host:port/db_index``.
"""
