# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Test example app."""

import os
import signal
import subprocess
import time

import pytest

from invenio_sse import current_sse


@pytest.yield_fixture
def example_app():
    """Example app fixture."""
    current_dir = os.getcwd()
    # go to example directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exampleappdir = os.path.join(project_dir, 'examples')
    os.chdir(exampleappdir)
    # Starting example web app
    cmd = 'FLASK_APP=app.py flask run --debugger -p 5000 -h 0.0.0.0'
    webapp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              preexec_fn=os.setsid, shell=True)
    time.sleep(10)
    # return webapp
    yield webapp
    # stop server
    os.killpg(webapp.pid, signal.SIGTERM)
    # return to the original directory
    os.chdir(current_dir)


def test_example_app(example_app, app):
    """Test example app."""
    with app.test_request_context():
        cmd = 'curl http://0.0.0.0:5000/sse?channel=project-1 --max-time 5'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        time.sleep(1)
        current_sse.publish(data='hello world', channel='project-1',
                            type_='edit', retry=123, id_=456)
        out, err = p.communicate()

        assert 'hello world' in out.decode('utf-8')
        assert 'event:edit' in out.decode('utf-8')
