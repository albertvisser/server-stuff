"""INVoke commands related to CherryPy server administration
"""
import os.path
from invoke import task
from config import HOME, runpath
from tasks_shared import report_result, check_result, remove_result

allproj = ('rst2html_fs', 'logviewer', 'magiokis-cherry', 'rst2html_mongo', 'rst2html_postgres')


@task(help={'names': 'comma-separated list of server names'})
def stop(c, names=None):
    "stop indicated cherrypy server(s)"
    names = names.split(',') if names else allproj  # _get_cherry_parms()
    for proj in names:
        pid = _get_cherry_parms(proj)[3]
        if os.path.exists(pid):
            c.run(f'sudo kill -s SIGKILL `cat {pid}`')
            c.run(f'sudo rm -f {pid}')
            remove_result(c, proj)


@task(help={'names': 'comma-separated list of server names'})
def start(c, names=None):
    "start indicated cherrypy server(s) (through cherryd)"
    names = names.split(',') if names else allproj  # _get_cherry_parms()
    for proj in names:
        result = check_result(proj)
        if result:
            print(f'{proj} {result}')
            continue
        conf, pad, prog, pid, _ = _get_cherry_parms(proj)
        with c.cd(pad):
            # result = c.run('sudo /usr/bin/cherryd3 '
            result = c.run(f'sudo /usr/bin/cherryd -c {conf} -d -p {pid} -i {prog}')
            report_result(proj, result)


@task(help={'names': 'comma-separated list of server names'})
def restart(c, names=None):
    "restart cherrypy site (arg:project)"
    names = names.split(',') if names else allproj  # _get_cherry_parms()
    for proj in names:
        stop(c, proj)
        start(c, proj)


@task
def list_servers(c):
    "list of cherrypy server names"
    print("Available CherryPy projects: " + ", ".join(allproj))


def _get_cherry_parms(project):
    origproj = project
    pad = os.path.join(HOME, 'projects', project)
    if project == allproj[2]:
        project = project.split('-')[0]
        pad = pad.replace('projects', 'projects/.frozen')
    elif project.startswith(allproj[0].split('_', 1)[0]):
        pad = os.path.join(HOME, 'projects', allproj[0].split('_', 1)[0])
    conf = f'{project}.conf'
    prog = f'start_{project}'
    pid = os.path.join(runpath, f'{project}.pid')
    sock = os.path.join(runpath, f'{project}.sock')
    if origproj == allproj[2]:
        pid = os.path.join(runpath, f'{project}c.pid')
        sock = os.path.join(runpath, f'{project}c.sock')
    return conf, pad, prog, pid, sock


def get_projectnames():
    "return all cherrypy project names"
    return allproj


def get_pid(project):
    "return the process id used for a project server"
    return _get_cherry_parms(project)[3]
