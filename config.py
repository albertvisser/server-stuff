"""constants and such for invoke tasks
"""
import os.path
import collections

HERE = os.path.dirname(__file__)
INIT, NGINX, APACHE = '/etc/init.d', '/etc/nginx', '/etc/apache2'
PHP = '/etc/php/7.0/fpm/'
AVL, NBL = 'sites-available', 'sites-enabled'
AVAIL = os.path.join(NGINX, AVL)
ENABL = os.path.join(NGINX, NBL)
A_AVAIL = os.path.join(APACHE, AVL)
A_ENABL = os.path.join(APACHE, NBL)
runpath, HOME = '/var/run', '/home/albert'
HGWEB = os.path.join(HOME, 'www', 'hgweb')
# hgweb_pid = os.path.join(runpath, 'hgwebdir.pid')
# hgweb_sock = os.path.join(runpath, 'hgwebdir.sock')
TRAC = os.path.join(HOME, 'lemontrac')
# project = os.path.basename(TRAC)
# trac_pid = os.path.join(runpath, '{}.pid'.format(project))
# trac_sock = os.path.join(runpath, '{}.sock'.format(project))
confpath = os.path.join(HERE, 'nginx')
intconf = collections.defaultdict(list)
for conf in os.listdir(confpath):
    with open(os.path.join(confpath, conf)) as _in:
        for line in _in:
            if line.strip().startswith('server_name'):
                test = line.split('server_name', 1)
                name = test[1].split(';')[0].strip()
                intconf[conf].append(name)
# django_sites = ['magiokis', 'actiereg', 'myprojects', 'mydomains', 'myapps', 'albums']
# django_project_path = {x: os.path.join(HOME, 'projects', x) for x in django_sites}
# django_project_path['magiokis'] += '-django'
# PLONEDIR = os.path.join(HOME, 'Plone', 'zinstance')
PLONES = ('plone',)
extconf = {'nginx': (NGINX, True, '@.conf'),
           'fcgiwrap': (NGINX, True, 'fcgiwrap.conf'),
           'php': (PHP, True, '@.ini'),
           'hgweb': (HGWEB, False, '@-config'),
           'trac-conf': (os.path.join(TRAC, 'conf'), False, 'trac.ini'),
           # 'plone-conf': (PLONEDIR, False, 'buildout.cfg'),
           'hosts': ('/etc', True, '@'),
           'apache2': (APACHE, True, '@.conf'),
           'ports': (APACHE, True, '@.conf'),
           ## 'php-fcgi': (INIT, True, '@'),
           'rc.local': ('/etc', True, '@'),
           'hgweb-srv': (HGWEB, False, 'hgweb.fcgi'),
           ## 'hgweb.cgi': (HGWEB, False, '@'),
           ## 'hgweb.wsgi': (HGWEB, False, '@'),
           'trac-srv': (TRAC, False, 'tracwsgi.py')}
for plone in PLONES:
    extconf['{}-buildout'.format(plone)] = (os.path.join(HOME, '{}/zinstance'.format(
        plone.title())), False, 'buildout.cfg')
# EDITORCMD = 'SciIE {} &'
EDITORCMD = "gnome-terminal --profile='Code Editor Shell' -- vi {} &"
