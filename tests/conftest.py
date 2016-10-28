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


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import tempfile
from time import sleep

import pytest
from elasticsearch import RequestError
from flask import Flask
from flask.cli import ScriptInfo
from flask_babelex import Babel
from flask_breadcrumbs import Breadcrumbs
from flask_celeryext import FlaskCeleryExt
from flask_cli import FlaskCLI
from flask_login import login_user
from flask_oauthlib.provider import OAuth2Provider
from invenio_access import InvenioAccess
from invenio_access.models import ActionUsers
from invenio_accounts import InvenioAccounts
from invenio_accounts.views import blueprint as accounts_blueprint
from invenio_assets import InvenioAssets
from invenio_db import db as db_
from invenio_db import InvenioDB
from invenio_deposit import InvenioDeposit, InvenioDepositREST
from invenio_deposit.api import Deposit
from invenio_files_rest import InvenioFilesREST
from invenio_files_rest.models import Location
from invenio_indexer import InvenioIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_oauth2server import InvenioOAuth2Server, InvenioOAuth2ServerREST
from invenio_oauth2server.views import \
    settings_blueprint as oauth2server_settings_blueprint
from invenio_pidstore import InvenioPIDStore
from invenio_records import InvenioRecords
from invenio_records_rest import InvenioRecordsREST
from invenio_records_rest.utils import PIDConverter
from invenio_records_ui import InvenioRecordsUI
from invenio_search import InvenioSearch, current_search, current_search_client
from invenio_search_ui import InvenioSearchUI
from mock import patch
from sqlalchemy_utils import create_database, database_exists

from invenio_sse import InvenioSSE
from invenio_sse.contrib.deposit import InvenioSSEDeposit


@pytest.yield_fixture()
def app():
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    app = Flask('testapp', instance_path=instance_path)
    app.config.update(
        TESTING=True
    )
    InvenioSSE(app)

    with app.app_context():
        yield app

    shutil.rmtree(instance_path)


@pytest.yield_fixture()
def app_deposit():
    """App configuration for using InvenioDeposit."""
    instance_path = tempfile.mkdtemp()
    app = Flask('testapp', instance_path=instance_path)
    app.config.update(
        TESTING=True,
        CELERY_ALWAYS_EAGER=True,
        CELERY_CACHE_BACKEND='memory',
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_RESULT_BACKEND='cache',
        JSONSCHEMAS_URL_SCHEME='http',
        SECRET_KEY='CHANGE_ME',
        SECURITY_PASSWORD_SALT='CHANGE_ME_ALSO',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SQLALCHEMY_ECHO=False,
        WTF_CSRF_ENABLED=False,
        DEPOSIT_SEARCH_API='/api/search',
        SECURITY_PASSWORD_HASH='plaintext',
        SECURITY_PASSWORD_SCHEMES=['plaintext'],
        SECURITY_DEPRECATED_PASSWORD_SCHEMES=[],
        OAUTHLIB_INSECURE_TRANSPORT=True,
        OAUTH2_CACHE_TYPE='simple',
    )
    app.url_map.converters['pid'] = PIDConverter
    FlaskCLI(app)
    Babel(app)
    FlaskCeleryExt(app)
    InvenioDB(app)
    Breadcrumbs(app)
    InvenioAccounts(app)
    InvenioAccess(app)
    app.register_blueprint(accounts_blueprint)
    InvenioAssets(app)
    InvenioJSONSchemas(app)
    InvenioSearch(app)
    InvenioRecords(app)
    app.url_map.converters['pid'] = PIDConverter
    InvenioRecordsREST(app)
    InvenioPIDStore(app)
    InvenioIndexer(app)
    InvenioDeposit(app)
    InvenioSearchUI(app)
    InvenioRecordsUI(app)
    InvenioFilesREST(app)
    OAuth2Provider(app)
    InvenioOAuth2Server(app)
    InvenioOAuth2ServerREST(app)
    app.register_blueprint(oauth2server_settings_blueprint)
    InvenioDepositREST(app)
    InvenioSSE(app)

    with app.app_context():
        yield app


@pytest.yield_fixture()
def db(app_deposit):
    """Database fixture."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.yield_fixture()
def es(app_deposit):
    """Elasticsearch fixture."""
    try:
        list(current_search.create())
    except RequestError:
        list(current_search.delete(ignore=[404]))
        list(current_search.create(ignore=[400]))
    current_search_client.indices.refresh()
    yield current_search_client
    list(current_search.delete(ignore=[404]))


@pytest.fixture()
def location(app_deposit, db):
    """Create default location."""
    tmppath = tempfile.mkdtemp()
    with db.session.begin_nested():
        Location.query.delete()
        loc = Location(name='local', uri=tmppath, default=True)
        db.session.add(loc)
    db.session.commit()
    return location


@pytest.fixture()
def deposit(app_deposit, es, users, location, db):
    """New deposit with files."""
    record = {
        'title': 'fuu'
    }
    with app_deposit.test_request_context():
        login_user(users[0])
        deposit = Deposit.create(record)
        deposit.commit()
        db.session.commit()
    sleep(2)
    return deposit


@pytest.fixture()
def users(app_deposit, db):
    """Create users."""
    with db.session.begin_nested():
        datastore = app_deposit.extensions['security'].datastore
        user1 = datastore.create_user(email='info@inveniosoftware.org',
                                      password='tester', active=True)
        user2 = datastore.create_user(email='test@inveniosoftware.org',
                                      password='tester2', active=True)
        admin = datastore.create_user(email='admin@inveniosoftware.org',
                                      password='tester3', active=True)
        # Assign deposit-admin-access to admin only.
        db.session.add(ActionUsers(
            action='deposit-admin-access', user=admin
        ))
    db.session.commit()
    return [user1, user2]


@pytest.fixture()
def script_info(app):
    """Get ScriptInfo object for testing CLI."""
    return ScriptInfo(create_app=lambda info: app)


@pytest.fixture()
def deposit_integration(app_deposit):
    """Integrate SSE with Invenio-Deposit."""
    class MockedEntryPoint:
        def __init__(self):
            self.name = 'deposit'

        def load(self):
            return InvenioSSEDeposit

    with patch('pkg_resources.iter_entry_points') as iter:
        mocked_entry_point = MockedEntryPoint()
        iter.return_value = [mocked_entry_point]
        app_deposit.extensions['invenio-sse'].load_integration('mocked')
