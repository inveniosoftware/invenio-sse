# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""SSE extension for InvenioDeposit."""

from __future__ import absolute_import, print_function

import pkg_resources

from .rest import create_blueprint


class InvenioSSEDeposit(object):
    """Invenio-Deposit SSE extension."""

    def __init__(self, app=None):
        """Extension initialization.

        :param app: An instance of :class:`flask.Flask`.
        """
        # Check that Invenio-Deposit is installed.
        try:
            pkg_resources.get_distribution('invenio_deposit')
        except pkg_resources.DistributionNotFound:
            raise RuntimeError(
                'You must use `pip install invenio-sse[deposit]` to '
                'enable the SSE integration with Invenio-Deposit.')

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization.

        Initialize the REST endpoints for SSE.

        :param app: An instance of :class:`flask.Flask`.
        """
        blueprint = create_blueprint(
            app.config['DEPOSIT_REST_ENDPOINTS']
        )

        app.register_blueprint(blueprint)
