#!/usr/bin/env python
"""gunicorn variant
"""
import sys
import os

sys.stdout = sys.stderr

#put here your ENV's Variables
## sockaddr = '/home/albert/run/lemontrac.sock'
os.environ['TRAC_ENV'] = '/home/albert/lemontrac'
## # here is an example with multiple instances
## os.environ['TRAC_ENV_PARENT_DIR'] = '/home/albert/lemontrac/'
os.environ['PYTHON_EGG_CACHE'] = '/home/albert/lemontrac/eggs/'

## import trac.web.main
## application = trac.web.main.dispatch_request

import trac.web.standalone
import trac.web.main

def application(environ, start_application):
    environ['REMOTE_USER'] = environ.get('HTTP_REMOTE_USER')
    return trac.web.main.dispatch_request(environ, start_application)
    ## auth = {"lemontrac" : trac.web.main.BasicAuthentication(
        ## os.path.join(os.environ['TRAC_ENV'], "trac_users"), "lemontrac")}
    ## wsgi_app = trac.web.standalone.AuthenticationMiddleware(dispatch_request, auth)
    ## return wsgi_app(environ, start_application)
