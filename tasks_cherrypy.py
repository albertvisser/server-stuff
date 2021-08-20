"""INVoke commands related to CherryPy server administration
"""
import os.path
from invoke import task
from config import HOME, runpath
from tasks_shared import report_result, remove_result

allproj = ('rst2html_fs', 'logviewer', 'magiokis-cherry', 'rst2html_mongo', 'rst2html_postgres')


def _get_cherry_parms(project=None):
    if not project:
        return allproj
    origproj = project
    pad = os.path.join(HOME, 'projects', project)
    if project == allproj[2]:
        project = project.split('-')[0]
        pad = pad.replace('projects', 'projects/.frozen')
    elif project.startswith(allproj[0].split('_')[0]):
        pad = os.path.join(HOME, 'projects', allproj[0].split('_')[0])
    conf = '{}.conf'.format(project)
    prog = 'start_{}'.format(project)
    pid = os.path.join(runpath, '{}.pid'.format(project))
    sock = os.path.join(runpath, '{}.sock'.format(project))
    if origproj == allproj[2]:
        pid = os.path.join(runpath, '{}c.pid'.format(project))
        sock = os.path.join(runpath, '{}c.sock'.format(project))
    return conf, pad, prog, pid, sock


def get_projectnames():
    return allproj


def get_pid(project):
    return _get_cherry_parms(project)[3]


@task(help={'names': 'comma-separated list of server names'})
def stop(c, names=None):
    "stop indicated cherrypy server(s)"
    if not names:
        names = _get_cherry_parms()
    else:
        names = names.split(',')
    for proj in names:
        pid = _get_cherry_parms(proj)[3]
        if os.path.exists(pid):
            c.run('sudo kill -s SIGKILL `cat {}`'.format(pid))
            c.run('sudo rm -f {}'.format(pid))
            remove_result(c, proj)


@task(help={'names': 'comma-separated list of server names'})
def start(c, names=None):
    "start indicated cherrypy server(s) (through cherryd)"
    if not names:
        names = _get_cherry_parms()
    else:
        names = names.split(',')
    for proj in names:
        conf, pad, prog, pid, _ = _get_cherry_parms(proj)
        with c.cd(pad):
            # result = c.run('sudo /usr/bin/cherryd3 '
            result = c.run('sudo /usr/local/bin/cherryd '
                           '-c {} -d -p {} -i {}'.format(conf, pid, prog))
            report_result(proj, result)


@task(help={'names': 'comma-separated list of server names'})
def restart(c, names=None):
    "restart cherrypy site (arg:project)"
    if not names:
        names = _get_cherry_parms()
    else:
        names = names.split(',')
    for proj in names:
        stop(c, proj)
        start(c, proj)


@task
def list_servers(c):
    "list of cherrypy server names"
    print("Available CherryPy projects: " + ", ".join(_get_cherry_parms()))
