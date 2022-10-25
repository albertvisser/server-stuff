"""INVoke commands related to Django server administration
"""
import os
# import shutil
from invoke import task
from config import HOME, runpath
from tasks_shared import report_result, remove_result
django_sites = ['magiokis', 'actiereg', 'myprojects', 'mydomains', 'myapps', 'albums']
django_project_path = {x: os.path.join(HOME, 'projects', x) for x in django_sites}
django_project_path['magiokis'] = django_project_path['magiokis'].replace('projects',
                                                                          'projects/.frozen')
django_project_path['magiokis'] += '-django'


@task(help={'names': 'comma-separated list of server names'})
def stop(c, names=''):
    "stop indicated Django server(s)"
    if not names:
        names = django_project_path.keys()
    else:
        names = names.split(',')
    for proj in names:
        django_pid = _get_django_args(proj)[0]
        if os.path.exists(django_pid):
            c.run(f'sudo kill `cat {django_pid}`')
            c.run(f'sudo rm -f {django_pid}')
            remove_result(c, proj)


@task(help={'names': 'comma-separated list of server names'})
def start(c, names=None):
    """start indicated Django server(s) using manage.py
    (Python 2 used fastcgi, see version history; Python uses Gunicorn)
    """
    if names is None:
        names = sorted(django_project_path.keys())
    else:
        names = names.split(',')
    for proj in names:
        pid, sock, path = _get_django_args(proj)
        with c.cd(path):
            result = c.run(f'sudo /usr/bin/gunicorn -D -b unix:{sock} -p {pid} '
                           f'{proj}.wsgi:application')
            report_result(proj, result)


@task(help={'names': 'comma-separated list of server names'})
def restart(c, names=None):
    "restart django indicated server(s)"
    if names is None:
        names = django_project_path.keys()
    else:
        names = names.split(',')
    for proj in names:
        stop(c, proj)
        start(c, proj)


@task
def list_servers(c):
    "list of django server names"
    print("Available Django projects: " + ", ".join(django_project_path.keys()))


def get_django_admin_loc(c):
    "return location of django-admin program"
    django_loc = c.run('python -c "import django; print(django.__path__)"', hide=True)
    django_admin_loc = os.path.join(django_loc, 'contrib/admin/static/admin')
    return django_admin_loc


@task(help={'names': 'comma-separated list of server names'})
def link_admin_css(c, names=None, force=False):
    "add symlink to admin CSS for Django project"
    if names is None:
        names = django_project_path.keys()
    else:
        names = names.split(',')
    for project in names:
        path = _get_django_args(project)[2]
        skip = False
        # maak indien nog niet aanwezig directory static onder site root
        test = os.path.join(path, 'static')
        skip = False
        if os.path.exists(test):
            if os.path.exists(os.path.join(test, 'admin')):
                skip = True
            else:
                if not os.path.isdir(test):
                    os.remove(test)
        else:
            os.mkdir(test)
        if force or not skip:
            with c.cd(test):
                c.run(f'ln -s {get_django_admin_loc(c)}')


def _get_django_args(project):
    "return process id, socket name and file path for a project"
    return (os.path.join(runpath, f'{project}.pid'),
            os.path.join(runpath, f'{project}.sock'),
            django_project_path[project])


def get_projectnames():
    "return all django project names"
    return django_project_path.keys()


def get_pid(project):
    "return process id for django project server"
    return _get_django_args(project)[0]
