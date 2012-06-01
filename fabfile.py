import os
import shutil
from fabric.api import local, sudo, lcd
"""collection of shortcut functions concerning deployment
of my local ngnix stuff
includes:
- add/modify/remove configuration files
- start/stop/restart nginx server
- start/stop/restart mercurial server (hgweb)
- start/stop/restart trac server (tracd)
- start/stop/restart django servers (manage.py runfcgi)
- start/stop/restart cherrypy server(s) (cherryd)
"""

HERE = os.path.dirname(__file__)
AVAIL = '/etc/nginx/sites-available'
ENABL = '/etc/nginx/sites-enabled'
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

def addconf(name):
    "enable new configuration by creating symlink"
    oldname = os.path.join(AVAIL, name)
    newname = os.path.join(ENABL, name)
    ## os.symlink(oldname, newname)
    local('sudo ln -s {} {}'.format(oldname, newname))

def addconfs(*names):
    "addconf for multiple names provided as a comma separated string"
    for conf in names:
        addconf(conf.strip())

def modconf(name):
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

def modconfs(*names):
    "modconf for multiple names provided as a comma separated string"
    for conf in names:
        modconf(conf.strip())

def rmconf(name):
    "disable configuration by removing symlink"
    newname = os.path.join(ENABL, name)
    ## os.remove(name)
    local(' sudo rm {}'.format(newname))

def rmconfs(*names):
    "rmconf for multiple names provided as a comma separated string"
    for conf in names:
        rmconf(conf.strip())

def stop_nginx():
    local('sudo /etc/init.d/nginx stop')

def start_nginx():
    local('sudo /etc/init.d/nginx start')

def restart_nginx():
    "restart nginx"
    local('sudo killall -HUP nginx')

def stop_hgweb():
    local('sudo kill `cat {}`'.format(hgweb_pid))

def start_hgweb():
    start = os.path.join(HGWEB, 'hgweb.fcgi')
    local('sudo spawn-fcgi -f {} -s {} -P {} -u {}'.format(start, hgweb_sock,
        hgweb_pid, 'www-data'))

def restart_hgweb():
    "restart hgweb after editing configuration or startup script"
    stop_hgweb()
    start_hgweb()

def stop_trac():
    local('sudo kill `cat {}`'.format(trac_pid))

def start_trac():
    start = os.path.join(TRAC, 'trac.fcgi')
    auth = '{},{},{}'.format(project,os.path.join(TRAC,'trac_users'),project)
    local('sudo tracd -d -p 9000 --pidfile {} -s {} --basic-auth="{}"'.format(
        trac_pid, TRAC, auth))
    ## local('sudo spawn-fcgi -f {} -s {} -P {} -u {}'.format(start, trac_sock,
        ## trac_pid, 'www-data'))

def restart_trac():
    "restart trac after editing configuration or startup script"
    stop_trac()
    start_trac()

def _get_django_args(project):
    return (os.path.join(runpath, '{}.pid'.format(project)),
        os.path.join(runpath, '{}.sock'.format(project)),
        django_project_path[project])

def stop_django(project):
    django_pid, _, _ = _get_django_args(project)
    if os.path.exists(django_pid):
        local('sudo kill `cat {}`'.format(django_pid))
        local('sudo rm -f {}'.format(django_pid))

def start_django(*project):
    def start(path, sock, pid):
        local('sudo python {}/manage.py runfcgi socket={} pidfile={}'.format(path,
            sock, pid))
        local('sudo chown www-data {}'.format(sock))
    if not project:
        project = django_project_path.keys()
    for proj in project:
        pid, sock, path = _get_django_args(proj)
        start(path, sock, pid)

def restart_django(project):
    "restart django site (arg:project)"
    stop_django(project)
    start_django(project)

def _get_cherry_parms(project):
    # voorlopig even alleen rst2html
    if project == 'rst2html':
        pad = '/home/albert/rst2html-web'
        ## conf = os.path.join(pad, 'rst2html.conf')
        conf = os.path.join(HERE, 'rst2html.conf')
        ## prog = 'rst2html'
        prog = 'start_rst2html'
        pid = os.path.join(runpath, '{}.pid'.format(project))
        sock = os.path.join(runpath, '{}.sock'.format(project))
    elif project == 'bitbucket':
        pad = '/home/albert/www/bitbucket'
        conf = os.path.join(pad, 'rst2html.conf')
        prog = 'start_bitbucket'
        pid = os.path.join(runpath, '{}.pid'.format(project))
        sock = os.path.join(runpath, '{}.sock'.format(project))
    return conf, pad, prog, pid, sock

def stop_cherry(project='rst2html'):
    pid = _get_cherry_parms(project)[3]
    if os.path.exists(pid):
        local('sudo kill `cat {}`'.format(pid))
        local('sudo rm -f {}'.format(pid))

def start_cherry(project='rst2html'):
    conf, pad, prog, pid, _ = _get_cherry_parms(project)
    local('sudo cherryd -c {} -d -p {} -i {}'.format(conf, pid, prog))

def restart_cherry(project='rst2html'):
    "restart cherrypy site (arg:project)"
    stop_cherry(project)
    start_cherry(project)

def stop_logviewer():
    local("ps ux | awk '/ python viewlogs.py/ && !/awk/' > /tmp viewlogs.pid")
    data = ''
    with open('/tmp/viewlogs.pid') as _in:
        data = _in.read()
    if data:
        pid = data.split()[1]
        local('sudo kill {}'.format(pid))

def start_logviewer():
    with lcd('/home/albert/logviewer'):
        local('python viewlogs.py')

def restart_logviewer():
    stop_logviewer(project)
    start_logviewer(project)
