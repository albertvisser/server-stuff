#!/usr/bin/env python
"""gunicorn variant"""
import sys
import os

sys.stdout = sys.stderr

#put here your ENV's Variables
sockaddr = '/home/albert/run/lemontrac.sock'
os.environ['TRAC_ENV'] = '/home/albert/lemontrac'
## # here is an example with multiple instances
## os.environ['TRAC_ENV_PARENT_DIR'] = '/home/albert/lemontrac/'
## os.environ['PYTHON_EGG_CACHE'] = '/home/repos/projects/.eggs/'

import trac.web.main
application = trac.web.main.dispatch_request
