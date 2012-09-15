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
AVAIL = '/etc/nginx/sites-available'
ENABL = '/etc/nginx/sites-enabled'
A_AVAIL = '/etc/apache2/sites-available'
A_ENABL = '/etc/apache2/sites-enabled'
runpath = '/var/run'
HGWEB = '/home/albert/www/hgweb'
hgweb_pid = os.path.join(runpath, 'hgwebdir.pid')
hgweb_sock = os.path.join(runpath, 'hgwebdir.sock')
TRAC = '/home/albert/lemontrac'
project = os.path.basename(TRAC)
trac_pid = os.path.join(runpath, '{}.pid'.format(project))
trac_sock = os.path.join(runpath, '{}.sock'.format(project))
django_project_path = {
    'pythoneer': '/home/albert/www/django/pythoneer',
    'magiokis': '/home/albert/www/django/magiokis',
    'actiereg': '/home/albert/www/django/actiereg',
    'myprojects': '/home/albert/www/django/doctool',
    'mydomains': '/home/albert/www/testdjango/domainchecker',
    'myapps': '/home/albert/www/testdjango/myapps',
    }
extconf = {
    'fcgiwrap': ('/etc/nginx', True, '.conf'),
    'rst2html': ('/home/albert/rst2html-web', False, '.conf'),
    'rc.local': ('/etc', True, ''),
    'hosts': ('/etc', True, ''),
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
    local('sudo /etc/init.d/nginx stop')

def start_nginx():
    "start nginx"
    local('sudo /etc/init.d/nginx start')

def restart_nginx():
    "restart nginx"
    local('sudo killall -HUP nginx')

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
    auth = '{},{},{}'.format(project,os.path.join(TRAC,'trac_users'),project)
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

def restart_django(project):
    "restart django indicated server(s)"
    stop_django(project)
    start_django(project)

def _get_cherry_parms(project):
    if project == 'rst2html':
        pad = '/home/albert/rst2html-web'
        ## conf = os.path.join(pad, 'rst2html.conf')
        conf = os.path.join(HERE, 'rst2html.conf')
        ## prog = 'rst2html'
        prog = 'start_rst2html'
        pid = os.path.join(runpath, '{}.pid'.format(project))
        sock = os.path.join(runpath, '{}.sock'.format(project))
    elif project == 'logviewer':
        pad = '/home/albert/logviewer'
        conf = os.path.join(HERE, 'logviewer.conf')
        prog = 'start_logviewer'
        pid = os.path.join(runpath, '{}.pid'.format(project))
        sock = os.path.join(runpath, '{}.sock'.format(project))
    elif project == 'magiokis':
        pad = '/home/albert/www/cherrypy/magiokis'
        conf = os.path.join(pad, 'magiokis.conf')
        prog = 'start_magiokis'
        pid = os.path.join(runpath, '{}c.pid'.format(project))
        sock = os.path.join(runpath, '{}.sock'.format(project))
    return conf, pad, prog, pid, sock

def stop_cherry(*project):
    "stop indicated cherrypy server(s)"
    if not project:
        project = ('rst2html', 'logviewer', 'magiokis')
    for proj in project:
        pid = _get_cherry_parms(proj)[3]
        if os.path.exists(pid):
            local('sudo kill -s SIGKILL `cat {}`'.format(pid))
            local('sudo rm -f {}'.format(pid))

def start_cherry(*project):
    "start indicated cherrypy server(s) (through cherryd)"
    if not project:
        project = ('rst2html', 'logviewer', 'magiokis')
    for proj in project:
        conf, pad, prog, pid, _ = _get_cherry_parms(proj)
        local('sudo cherryd -c {} -d -p {} -i {}'.format(conf, pid, prog))

def restart_cherry(project):
    "restart cherrypy site (arg:project)"
    stop_cherry(project)
    start_cherry(project)

def start_plone():
    with lcd('/home/albert/Plone/zinstance'):
        local('bin/plonectl start')

def stop_plone():
    with lcd('/home/albert/Plone/zinstance'):
        local('bin/plonectl stop')

def restart_plone():
    stop_plone()
    start_plone()

def stop_apache():
    "stop apache"
    local('sudo /etc/init.d/apache stop')

def start_apache():
    "start apache"
    local('sudo /etc/init.d/apache start')

def restart_apache():
    "restart apache"
    local('sudo /etc/init.d/apache restart')

def addconf_apache(*names):
    for conf in names:
        oldname = os.path.join(A_AVAIL, conf)
        newname = os.path.join(A_ENABL, conf)
        local('sudo ln -s {} {}'.format(oldname, newname))

def modconf_apache(*names):
    for conf in names:
        oldname = os.path.join(HERE, 'apache2', name)
        local('sudo cp {} {}'.format(oldname, A_AVAIL))

def rmconf_apache(*names):
    for conf in names:
        newname = os.path.join(A_ENABL, name)
        local(' sudo rm {}'.format(newname))
