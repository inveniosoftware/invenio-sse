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
