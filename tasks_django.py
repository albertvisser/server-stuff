"""INVoke commands related to Django server administration
"""
import os
# import shutil
from invoke import task
from config import HOME, runpath
from tasks_shared import report_result, check_result, remove_result
# django_sites = ['magiokis', 'actiereg', 'myprojects', 'mydomains', 'myapps', 'albums']
django_sites = ['actiereg', 'myprojects', 'mydomains', 'myapps', 'albums']
django_project_path = {x: os.path.join(HOME, 'projects', x) for x in django_sites}
# django_project_path['magiokis'] = django_project_path['magiokis'].replace('projects',
#                                                                           'projects/.frozen')
# django_project_path['magiokis'] += '-django'


@task(help={'names': 'comma-separated list of server names'})
def stop(c, names=''):
    "stop indicated Django server(s)"
    names = names.split(',') if names else django_project_path.keys()
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
    names = names.split(',') if names else django_project_path.keys()
    for proj in names:
        result = check_result(proj)
        if result:
            print(f'{proj} {result}')
            continue
        pid, sock, path = _get_django_args(proj)
        with c.cd(path):
            result = c.run(f'sudo /usr/bin/gunicorn -D -b unix:{sock} -p {pid} '
                           f'{proj}.wsgi:application')
            report_result(proj, result)


@task(help={'names': 'comma-separated list of server names'})
def restart(c, names=None):
    "restart django indicated server(s)"
    names = names.split(',') if names else django_project_path.keys()
    for proj in names:
        stop(c, proj)
        start(c, proj)


@task
def list_servers(c):
    "list of django server names"
    print("Available Django projects: " + ", ".join(django_project_path.keys()))


def get_django_admin_loc(c):
    "return location of django-admin program"
    django_loc = c.run('python -c "import django; print(django.__path__)"', hide=True).stdout
    django_loc = django_loc.split("'")[1]
    django_admin_loc = os.path.join(django_loc, 'contrib/admin/static/admin')
    return django_admin_loc


@task(help={'names': 'comma-separated list of server names'})
def link_admin_css(c, names=None, force=False):
    "add symlink to admin CSS for Django project"
    names = names.split(',') if names else django_project_path.keys()
    dest = get_django_admin_loc(c)
    for project in names:
        path = _get_django_args(project)[2]
        # maak indien nog niet aanwezig directory static onder site root
        staticdir = os.path.join(path, 'static')
        skip = False
        if os.path.exists(staticdir):
            if os.path.exists(os.path.join(staticdir, 'admin')):
                skip = True
                if force:
                    os.remove(os.path.join(staticdir, 'admin'))
                    skip = False
            elif not os.path.isdir(staticdir):
                os.remove(staticdir)
        else:
            os.mkdir(staticdir)
        if not skip:
            with c.cd(staticdir):
                c.run(f'ln -s {dest}')


@task
def check_admin_links(c):
    "After a Python or Django upgrade, check if sumlinks to admin css need to be upgraded also"
    admin_loc = get_django_admin_loc(c)
    for project in django_project_path:
        print(f'For project {project}:')
        recreate = False
        path = _get_django_args(project)[2]
        staticdir = os.path.join(path, 'static')
        admin_link = os.path.join(staticdir, 'admin')
        print(f'  looking for {admin_link}')
        if os.path.islink(admin_link):
            if os.path.exists(admin_link):
                admin_path = os.readlink(admin_link)
                print(f'  symlink found pointing to {admin_path}', end='')
                ok = admin_path == admin_loc
            else:
                print('  symlink found pointing to invalid location', end='')
                ok = False
            if ok:
                print(', all is well.')
            else:
                print(', removing and', end= '')
                os.remove(admin_link)
                recreate = True
        else:
            if os.path.exists(admin_link):
                print('  admin found but not a symlink, renaming and', end='')
                os.rename(admin_link, admin_link + '.old')
                recreate = True
            else:
                print('  no admin found,', end='')
                recreate = True
        if recreate:
            print(' creating new symlink')
            with c.cd(staticdir):
                c.run(f'ln -s {admin_loc}')


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
