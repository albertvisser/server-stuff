#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
## sys.stdout = sys.stderr
import cgitb
cgitb.enable()
import cherrypy

ROOT = '/home/albert/rst2html'
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from rst2html import Rst2Html


cherrypy.config.update({'environment': 'embedded'})

application = cherrypy.tree.mount(Rst2Html())
cherrypy.config.update({'engine.autoreload_on': False,
        })
