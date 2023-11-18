"""constants and such for invoke tasks
"""
import os.path
import collections

HERE = os.path.dirname(__file__)
INIT, NGINX, APACHE = '/etc/init.d', '/etc/nginx', '/etc/apache2'
PHP = '/etc/php7'
AVL, NBL = 'sites-available', 'sites-enabled'
AVAIL = os.path.join(NGINX, AVL)
ENABL = os.path.join(NGINX, NBL)
A_AVAIL = os.path.join(APACHE, AVL)
A_ENABL = os.path.join(APACHE, NBL)
sysctlpath = '/etc/systemd/system'
runpath, HOME = '/var/run', '/home/albert'
HGWEB = os.path.join(HOME, 'www', 'hgweb')
# hgweb_pid = os.path.join(runpath, 'hgwebdir.pid')
# hgweb_sock = os.path.join(runpath, 'hgwebdir.sock')
TRAC = os.path.join(HOME, 'lemontrac')
# project = os.path.basename(TRAC)
# trac_pid = os.path.join(runpath, '{}.pid'.format(project))
# trac_sock = os.path.join(runpath, '{}.sock'.format(project))
confpath = os.path.join(HERE, 'nginx')


def build_server_dict():
    "build a dictionary of lists of server names per server config"
    intconf = collections.defaultdict(list)
    for entry in os.scandir(confpath):  # for conf in os.listdir(confpath):
        if not entry.is_file():
            continue
        with open(entry.path) as _in:  # with open(os.path.join(confpath, conf)) as _in:
            for line in _in:
                if line.strip().startswith('server_name'):
                    test = line.split('server_name', 1)
                    name = test[1].split(';')[0].strip()
                    intconf[entry.name].append(name)   # intconf[conf].append(name)
    return intconf


intconf = build_server_dict()
# django_sites = ['magiokis', 'actiereg', 'myprojects', 'mydomains', 'myapps', 'albums']
# django_project_path = {x: os.path.join(HOME, 'projects', x) for x in django_sites}
# django_project_path['magiokis'] += '-django'
PLONEDIR = os.path.join(HOME, 'Plone', 'zinstance')
PLONES = ('plone',)
# mapping van config naam op tuple van doeldirectory, sudo_nodig, vervangpatroon voor filenaam
extconf = {'nginx': (NGINX, True, '@.conf'),
           'fcgiwrap': (NGINX, True, '@.conf'),
           'php': (PHP, True, '@.ini'),
           'gitweb': ('/etc', True, '@.conf'),
           'cgit': ('/etc', True, '@rc'),
           'cgitrepos': ('/etc', True, '@'),
           # 'hgweb': (HGWEB, False, '@-config'),
           'trac': (os.path.join(TRAC, 'conf'), True, 'trac.ini'),
           'plone-conf': (PLONEDIR, False, 'buildout.cfg'),
           'hosts': ('/etc', True, '@'),
           'apache2': (APACHE, True, '@.conf'),
           'ports': (APACHE, True, '@.conf'),
           # 'php-fcgi': (INIT, True, '@'),
           # 'rc.local': ('/etc', True, '@'),
           # 'hgweb-srv': (HGWEB, False, 'hgweb.fcgi'),
           # 'hgweb.cgi': (HGWEB, False, '@'),
           # 'hgweb.wsgi': (HGWEB, False, '@'),
           # 'trac-srv': (TRAC, False, 'tracwsgi.py')
           'lemontrac': (sysctlpath, True, 'lemontrac.service'),
           }
for plone in PLONES:
    extconf['{}-buildout'.format(plone)] = (os.path.join(HOME, '{}/zinstance'.format(
        plone.title())), False, 'buildout.cfg')
# EDITORCMD = 'SciIE {} &'
EDITORCMD = "gnome-terminal --profile='Code Editor Shell' -- vim {} &"

# voor tasks_sites.py (controle pagina's van webapps)
check_address = {'quick': {
                    'original.magiokis.nl': '/cgi-bin/mainscript.py',
                    'php.magiokis.nl': '/magiokis.php?section=OW&subsection=Home',
                    'cherrypy.magiokis.nl': '/ow/',
                    'songs.magiokis.nl': '/cgi-bin/lijstsongs.py',
                    'denk.magiokis.nl': '/cgi-bin/denk_select.py',
                    'dicht.magiokis.nl': '/cgi-bin/dicht_select.py',
                    'vertel.magiokis.nl': '/cgi-bin/vertel_select.py', },
                 'full': {
                    # platte html hoeft wat mij betreft niet meer dan index pagina
                    'lemoncurry': None,
                    'lemoncurry.nl': None,
                    'www.lemoncurry.nl': None,
                    'rstblog.lemoncurry.nl': None,
                    'bitbucket.lemoncurry.nl': None,
                    'bitbucket_mongo.lemoncurry.nl': None,
                    'oldlocal.magiokis.nl': None,
                    'data.magiokis.nl': None,
                    # Drupal en andere frameworks hoeft van mij ook niet
                    'ragingdragon.lemoncurry.nl': None,
                    'local.magiokis.nl': None,
                    'plone.lemoncurry.nl': None,
                    'hg.lemoncurry.nl': None,
                    'trac.lemoncurry.nl': None,
                    # platte CGI wel
                    'muziek.lemoncurry.nl': 'albums-cgi-urls.rst',
                    'absentie.lemoncurry.nl': 'absentie-urls.rst',
                    'doctool.lemoncurry.nl': 'doctool-urls.rst',
                    'original.magiokis.nl': 'original-urls.rst',
                    'songs.magiokis.nl': 'songs-urls.rst',
                    'denk.magiokis.nl': 'denk-urls.rst',
                    'dicht.magiokis.nl': 'dicht-urls.rst',
                    'vertel.magiokis.nl': 'vertel-urls.rst',
                    # php-cgi ook
                    'php.magiokis.nl': 'magiokis-php-urls.rst',
                    # Django wel
                    'mydomains.lemoncurry.nl': 'mydomains-urls.rst',
                    'myapps.lemoncurry.nl': 'myapps-urls.rst',
                    'myprojects.lemoncurry.nl': 'myprojects-urls.rst',
                    'actiereg.lemoncurry.nl': 'actiereg-urls.rst',
                    'albums.lemoncurry.nl': 'albums-urls.rst',
                    'django.magiokis.nl': 'magiokis-django-urls.rst',
                    # Cherrypy ook
                    'cherrypy.magiokis.nl': 'magiokis-cherry-urls.rst',
                    'rst2html.lemoncurry.nl': 'rst2html-urls.rst',
                    'rst2html_mongo.lemoncurry.nl': 'rst2html-urls.rst',
                    'logviewer.lemoncurry.nl': 'logviewer-urls.rst', }, }
