#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.stdout = sys.stderr

os.chdir('/home/albert/logviewer')
sys.path.insert(0, '/home/albert/logviewer')
import cherrypy
from viewlogs_cherry import Logviewer

import cgitb
cgitb.enable()

cherrypy.config.update({'environment': 'embedded'})

application = cherrypy.tree.mount(Logviewer())
cherrypy.config.update({'engine.autoreload_on': False,
        })
