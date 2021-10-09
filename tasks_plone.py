"""INVoke commands related to Plone server administration
"""
from invoke import task
from config import HOME, PLONES
from tasks_shared import report_result, remove_result
import os.path


def _plone(c, action, sitenames):
    def _doit(sitename, action):
        plonedir = os.path.join(HOME, '{}/zinstance'.format(sitename.title()))
        with c.cd(plonedir):
            if action == 'start':
                result = c.run('bin/plonectl start')
                report_result("plone", result)
            elif action == 'stop':
                c.run('bin/plonectl stop')
                remove_result(c, "plone")
            elif action == 'buildout':
                c.run('bin/buildout')
    if not sitenames:
        sitenames = PLONES
    else:
        sitenames = sitenames.split(',')
    for name in sitenames:
        _doit(name, action)


@task(help={'names': 'comma-separated list of server names'})
def start(c, names=''):
    "start Plone default instance"
    _plone(c, 'start', names)


@task(help={'names': 'comma-separated list of server names'})
def stop(c, names=''):
    "stop Plone default instance"
    _plone(c, 'stop', names)


@task(help={'names': 'comma-separated list of server names'})
def restart(c, names=''):
    "restart Plone default instance"
    stop(c, names)
    start(c, names)


@task(help={'sitenames': 'comma-separated list of server names'})
def buildout(c, names=''):
    """run buildout on Plone instance

    to be used in this combo (Invoke version):
        fabsrv modconf plone-conf plone.buildout plone.restart
    """
    _plone(c, 'buildout', names)
