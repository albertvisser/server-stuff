"""INVoke commands related to Plone server administration

Plone 6 heeft een front- en een backend
"""
from invoke import task
from config import HOME, PLONES
from tasks_shared import report_result, check_result, remove_result
import os.path


def _plone(c, action, sitenames):
    sitenames = sitenames.split(',') if sitenames else PLONES
    for name in sitenames:
        plonedir = os.path.join(HOME, f'{name.title()}/zinstance')
        with c.cd(plonedir):
            if action == 'start':
                result = c.run('bin/plonectl start')
                report_result("plone", result)
            elif action == 'stop':
                c.run('bin/plonectl stop')
                remove_result(c, "plone")
            elif action == 'buildout':
                c.run('bin/buildout')


@task(help={'names': 'comma-separated list of server names'})
def start(c, names=''):
    "start Plone default instance"
    result = check_result('plone')
    if result:
        print('plone ' + result)
        return
    # _plone(c, 'start', names)
    c.run("sudo docker run --name plone6-backend -e SITE=Plone -e CORS_ALLOW_ORIGIN='*' -d"
          " -p 8085:8085 plone/plone-backend:6.0")
    c.run("sudo docker run --name plone6-frontend --link plone6-backend:backend"
          " -e RAZZLE_API_PATH=http://localhost:8085/Plone"
          " -e RAZZLE_INTERNAL_API_PATH=http://backend:8085/Plone -d"
          " -p 8090:8090 plone/plone-frontend:latest")


@task(help={'names': 'comma-separated list of server names'})
def stop(c, names=''):
    "stop Plone default instance"
    # _plone(c, 'stop', names)
    c.run("sudo docker stop plone6-frontend && sudo docker rm plone6-frontend")
    c.run("sudo docker stop plone6-backend && sudo docker rm plone6-backend")



@task(help={'names': 'comma-separated list of server names'})
def restart(c, names=''):
    "restart Plone default instance"
    stop(c, names)
    start(c, names)


@task(help={'names': 'comma-separated list of server names'})
def buildout(c, names=''):
    """run buildout on Plone instance

    to be used in this combo (Invoke version):
        fabsrv modconf plone-conf plone.buildout plone.restart
    """
    _plone(c, 'buildout', names)
