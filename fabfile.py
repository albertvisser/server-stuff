# -*- coding: utf-8 -*-

import os
import shutil
from fabric.api import local, sudo, lcd
"""collection of shortcut functions concerning deployment
of my local ngnix stuff
includes:
- add/modify/remove configuration file(s)
- start/stop/restart nginx server
- start/stop/restart mercurial server (hgweb)
- start/stop/restart trac server (tracd)
- start/stop/restart django server(s) (manage.py runfcgi)
- start/stop/restart cherrypy server(s) (cherryd)
"""

HERE = os.path.dirname(__file__)
INIT, NGINX, APACHE = '/etc/init.d', '/etc/nginx', '/etc/apache2'
AVL, NBL = 'sites-available', 'sites-enabled'
AVAIL = os.path.join(NGINX, AVL)
ENABL = os.path.join(NGINX, NBL)
A_AVAIL = os.path.join(APACHE, AVL)
A_ENABL = os.path.join(APACHE, NBL)
runpath, HOME = '/var/run', '/home/albert'
HGWEB = os.path.join(HOME, 'www/hgweb')
hgweb_pid = os.path.join(runpath, 'hgwebdir.pid')
hgweb_sock = os.path.join(runpath, 'hgwebdir.sock')
TRAC = os.path.join(HOME, 'lemontrac')
project = os.path.basename(TRAC)
trac_pid = os.path.join(runpath, '{}.pid'.format(project))
trac_sock = os.path.join(runpath, '{}.sock'.format(project))
django_sites = ['pythoneer', 'magiokis', 'actiereg', 'myprojects', 'mydomains',
    'myapps']
django_project_path = {x: os.path.join(HOME, 'www/django', x) for x in
    django_sites}
extconf = {
    'fcgiwrap': (NGINX, True, '.conf'),
    'nginx': (NGINX, True, '.conf'),
    'php-fcgi': (INIT, True, ''),
    'rst2html': (os.path.join(HOME, 'rst2html-web'), False, '.conf'),
    'rc.local': ('/etc', True, ''),
    'hosts': ('/etc', True, ''),
    'apache2': (APACHE, True, '.conf'),
    'ports': (APACHE, True, '.conf'),
    'hgweb': (HGWEB, False, '-config'),
    'hgweb.cgi': (HGWEB, False, ''),
    'hgweb.fcgi': (HGWEB, False, ''),
    'hgweb.wsgi': (HGWEB, False, ''),
    'trac': (os.path.join(TRAC, 'conf'), False, '.ini'),
    }

def _addconf(name):
    "enable new configuration by creating symlink"
    oldname = os.path.join(AVAIL, name)
    newname = os.path.join(ENABL, name)
    ## os.symlink(oldname, newname)
    local('sudo ln -s {} {}'.format(oldname, newname))

def addconf(*names):
    """enable Nginx configuration for one or more (file) names
    provided as a comma separated string"""
    for conf in names:
        _addconf(conf.strip())

def _modconf(name):
    "copy configuration after editing"
    oldname = os.path.join(HERE, name)
    ## newname = os.path.join(AVAIL, name)
    ## shutil.copyfile(oldname, newname)
    if name in extconf:
        dest, uses_sudo, ext = extconf[name]
        fname = os.path.join(HERE, name + ext)
        local('{} cp {} {}'.format('sudo' if uses_sudo else '', fname, dest))
    else:
        local('sudo cp {} {}'.format(oldname, AVAIL))

def modconf(*names):
    "deploy modifications for Nginx configuration file(s)"
    if names[0] == "?":
        text = "Available non-Nginx confs: " + ", ".join(extconf.keys())
        print(text)
        return
    for conf in names:
        _modconf(conf.strip())

def _rmconf(name):
    "disable configuration by removing symlink"
    newname = os.path.join(ENABL, name)
    ## os.remove(name)
    local(' sudo rm {}'.format(newname))

def rmconf(*names):
    "disable Nginx configuration for one or more file names"
    for conf in names:
        _rmconf(conf.strip())

def stop_nginx():
    "stop nginx"
    local('sudo {}/nginx stop'.format(INIT))

def start_nginx():
    "start nginx"
    local('sudo {}/nginx start'.format(INIT))

def restart_nginx():
    "restart nginx"
    local('sudo killall -HUP nginx')

def stop_php():
    "stop php"
    local('sudo {}/php-fcgi stop'.format(INIT))

def start_php():
    "start php"
    local('sudo {}/php-fcgi start'.format(INIT))

def restart_php():
    "restart php"
    local('sudo {}/php-fcgi restart'.format(INIT))

def stop_hgweb():
    "stop local Mercurial web server"
    local('sudo kill `cat {}`'.format(hgweb_pid))

def start_hgweb():
    "start local Mercurial web server using hgweb.fcgi"
    start = os.path.join(HGWEB, 'hgweb.fcgi')
    local('sudo spawn-fcgi -f {} -s {} -P {} -u {}'.format(start, hgweb_sock,
        hgweb_pid, 'www-data'))

def restart_hgweb():
    "restart local Mercurial web server"
    stop_hgweb()
    start_hgweb()

def stop_trac():
    "stop local trac server"
    local('sudo kill `cat {}`'.format(trac_pid))

def start_trac():
    "start local trac server using tracd"
    start = os.path.join(TRAC, 'trac.fcgi')
    auth = '{},{},{}'.format(project,os.path.join(TRAC, 'trac_users'),project)
    local('sudo tracd -d -p 9000 --pidfile {} -s {} --basic-auth="{}"'.format(
        trac_pid, TRAC, auth))
    ## local('sudo spawn-fcgi -f {} -s {} -P {} -u {}'.format(start, trac_sock,
        ## trac_pid, 'www-data'))

def restart_trac():
    "restart local trac server"
    stop_trac()
    start_trac()

def _get_django_args(project):
    return (os.path.join(runpath, '{}.pid'.format(project)),
        os.path.join(runpath, '{}.sock'.format(project)),
        django_project_path[project])

def stop_django(*project):
    "stop indicated Django server(s)"
    def stop(project):
        django_pid, _, _ = _get_django_args(project)
        if os.path.exists(django_pid):
            local('sudo kill `cat {}`'.format(django_pid))
            local('sudo rm -f {}'.format(django_pid))
    if not project:
        project = django_project_path.keys()
    for proj in project:
        stop(proj)

def start_django(*project):
    "start indicated Django server(s) using manage.py over fastcgi"
    def start(project):
        pid, sock, path = _get_django_args(project)
        local('sudo python {}/manage.py runfcgi socket={} pidfile={}'.format(path,
            sock, pid))
        local('sudo chown www-data {}'.format(sock))
    if not project:
        project = django_project_path.keys()
    for proj in project:
        start(proj)

def restart_django(*project):
    "restart django indicated server(s)"
    if not project:
        project = django_project_path.keys()
    elif project[0] == "?":
        text = "Available Django projects: " + ", ".join(django_project_path.keys())
        print(text)
        return
    for proj in project:
        stop_django(proj)
        start_django(proj)

def _get_cherry_parms(project=None):
    allproj = ('rst2html', 'logviewer', 'magiokis')
    if not project:
        return allproj
    pad = os.path.join(HOME, project)
    conf = os.path.join(HERE, '{}.conf'.format(project))
    prog = 'start_{}'.format(project)
    pid = os.path.join(runpath, '{}.pid'.format(project))
    sock = os.path.join(runpath, '{}.sock'.format(project))
    if project == allproj[0]:
        pad += '-web'
    elif project == allproj[2]:
        pad = os.path.join(HOME, 'www/cherrypy/magiokis')
        conf = os.path.join(pad, '{}.conf'.format(project))
        pid = os.path.join(runpath, '{}c.pid'.format(project))
    return conf, pad, prog, pid, sock

def stop_cherry(*project):
    "stop indicated cherrypy server(s)"
    if not project:
        project = _get_cherry_parms()
    for proj in project:
        pid = _get_cherry_parms(proj)[3]
        if os.path.exists(pid):
            local('sudo kill -s SIGKILL `cat {}`'.format(pid))
            local('sudo rm -f {}'.format(pid))

def start_cherry(*project):
    "start indicated cherrypy server(s) (through cherryd)"
    if not project:
        project = _get_cherry_parms()
    for proj in project:
        conf, pad, prog, pid, _ = _get_cherry_parms(proj)
        with lcd(HERE):
            local('sudo cherryd -c {} -d -p {} -i {}'.format(conf, pid, prog))

def restart_cherry(project):
    "restart cherrypy site (arg:project)"
    if project == '?':
        text = "Available CherryPy projects: " + ", ".join(_get_cherry_parms())
        print(text)
        return
    stop_cherry(project)
    start_cherry(project)

def start_plone():
    "start Plone default instance"
    with lcd(os.path.join(HOME, 'Plone/zinstance')):
        local('bin/plonectl start')

def stop_plone():
    "stop Plone default instance"
    with lcd(os.path.join(HOME, 'Plone/zinstance')):
        local('bin/plonectl stop')

def restart_plone():
    "restart Plone default instance"
    stop_plone()
    start_plone()

def buildout_plone():
    "run buildout on Plone instance"
    with lcd(os.path.join(HOME, 'Plone/zinstance')):
        local('bin/buildout')

def stop_apache():
    "stop apache"
    local('sudo {}/apache2 stop'.format(INIT))

def start_apache():
    "start apache"
    local('sudo {}/apache2 start'.format(INIT))

def restart_apache():
    "restart apache"
    local('sudo {}/apache2 restart'.format(INIT))

def addconf_apache(*names):
    """enable Apache configuration for one or more (file) names
    provided as a comma separated string"""
    for conf in names:
        oldname = os.path.join(A_AVAIL, conf)
        newname = os.path.join(A_ENABL, conf)
        local('sudo ln -s {} {}'.format(oldname, newname))

def modconf_apache(*names):
    "deploy modifications for Apache configuration file(s)"
    for conf in names:
        oldname = os.path.join(HERE, 'apache', conf)
        local('sudo cp {} {}'.format(oldname, A_AVAIL))

def rmconf_apache(*names):
    "disable Apache configuration for one or more file names"
    for conf in names:
        newname = os.path.join(A_ENABL, name)
        local(' sudo rm {}'.format(newname))

def edit(name):
    "edit a file related to the server configuration"
    local("SciTE {} &".format(os.path.join(HERE, name)))
