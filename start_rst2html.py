#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.stdout = sys.stderr

os.chdir('/home/albert/rst2html-web')
sys.path.insert(0, '/home/albert/rst2html-web')
import cherrypy
from rst2html import Rst2Html

import cgitb
cgitb.enable()

cherrypy.config.update({'environment': 'embedded'})

application = cherrypy.tree.mount(Rst2Html())
cherrypy.config.update({'engine.autoreload_on': False,
        })
