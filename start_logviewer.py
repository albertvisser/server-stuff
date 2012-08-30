#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
#sys.stdout = sys.stderr
import cgitb
cgitb.enable()
import cherrypy

ROOT = '/home/albert/logviewer'
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from viewlogs_cherry import Logviewer


cherrypy.config.update({'environment': 'embedded'})

application = cherrypy.tree.mount(Logviewer())
cherrypy.config.update({'engine.autoreload_on': False,
        })
