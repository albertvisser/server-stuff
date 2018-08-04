# -*- coding: utf-8 -*-
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
from __future__ import print_function

import os
import glob
## import sys
import shutil
import requests
import datetime
import collections
from fabric.api import *  # local, sudo, lcd, hide, settings
from all_local_pages import check_address

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
hgweb_pid = os.path.join(runpath, 'hgwebdir.pid')
hgweb_sock = os.path.join(runpath, 'hgwebdir.sock')
TRAC = os.path.join(HOME, 'lemontrac')
project = os.path.basename(TRAC)
trac_pid = os.path.join(runpath, '{}.pid'.format(project))
trac_sock = os.path.join(runpath, '{}.sock'.format(project))
GUNI = os.path.join(HOME, 'www', 'gunicorn')
gproject = os.path.basename(GUNI)
guni_pid = os.path.join(runpath, '{}.pid'.format(gproject))
guni_sock = os.path.join(runpath, '{}.sock'.format(gproject))
intconfs = ['default', 'cherrypy', 'django', 'drupal', 'fastcgi', 'flatpages',
            'others', 'plone', 'php-sites', 'trac']
intconf = collections.defaultdict(list)
for conf in intconfs:
    with open(os.path.join(HERE, conf)) as _in:
        for line in _in:
            if line.strip().startswith('server_name'):
                test = line.split('server_name', 1)
                name = test[1].split(';')[0].strip()
                intconf[conf].append(name)
django_sites = ['magiokis', 'actiereg', 'myprojects', 'mydomains',
                'myapps', 'albums']
django_project_path = {x: os.path.join(HOME, 'projects', x) for x in
                       django_sites}
django_project_path['magiokis'] += '-django'
PLONEDIR = os.path.join(HOME, 'Plone', 'zinstance')
PLONES = ('plone',)
extconf = {'nginx': (NGINX, True, '@.conf'),
           'fcgiwrap': (NGINX, True, 'fcgiwrap.conf'),
           'php': (PHP, True, '@.ini'),
           'hgweb': (HGWEB, False, '@-config'),
           'trac-conf': (os.path.join(TRAC, 'conf'), False, 'trac.ini'),
           'plone-conf': (PLONEDIR, False, 'buildout.cfg'),
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


def addstartup(name):
    """add an init file to the system startup sequence

    register in the extconf dict with INIT as destination
    """
    local('sudo chmod +x {}/{}'.format(INIT, name))     # make sure it's executable
    local('sudo update-rc.d {} defaults'.format(name))  # add to defaults


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


def _rmconf(name):
    "disable configuration by removing symlink"
    newname = os.path.join(ENABL, name)
    ## os.remove(name)
    local(' sudo rm {}'.format(newname))


def rmconf(*names):
    "disable Nginx configuration for one or more file names"
    for conf in names:
        _rmconf(conf.strip())


def _modconf(name, backup=False, append=False):
    "copy configuration after editing"
    if append: backup = True
    if backup:
        today = datetime.datetime.today().strftime('%Y%m%d%H%M%S')

    if name in extconf:
        dest, needs_sudo, fname = extconf[name]
        fname = fname.replace('@', name)
    else:
        dest = AVAIL
        needs_sudo = True
        fname = name

    if backup:
        src = os.path.join(dest, fname)
        trg = os.path.join('backup', '-'.join((fname, today)))
        with lcd(HERE):
            local('cp {} {}'.format(src, trg))

    if append:
        tmp = fname + '~~'
        tmp2 = tmp + '~'
        with lcd(HERE):
            local('cp {} {}'.format(fname, tmp))
            local('cat {} {} > {}'.format(trg, fname, tmp2))
            local('mv -f {} {}'.format(tmp2, fname))

    with lcd(HERE):
        local('{} cp {} {}'.format('sudo' if needs_sudo else '', fname, dest))

    if append:
        with lcd(HERE):
            local('mv -f {} {}'.format(tmp, fname))


def modconf(*names):
    "deploy modifications for Nginx configuration file(s); replace version"
    for conf in names:
        _modconf(conf.strip())


def modconfb(*names):
    "modconf: backup & replace version"
    for conf in names:
        _modconf(conf.strip(), backup=True)


def modconfa(*names):
    "modconf: backup & append version"
    for conf in names:
        _modconf(conf.strip(), append=True)


def newconf(*names):
    """shortcut to define and enable a new Nginx config in one go
    """
    for conf in names:
        _modconf(conf.strip())
        _addconf(conf.strip())


def _diffconf(name, gui=False):
    "compare a configuration file"
    if name in extconf:
        dest, _, fname = extconf[name]
        if fname.startswith('@'):
            fname = name + fname[1:]
    else:
        dest, fname = AVAIL, name
    if gui:
        local('meld {} {}'.format(os.path.join(dest, fname),
                                  os.path.join(HERE, fname)))
    else:
        with settings(hide('warnings'), warn_only=True):
            local('diff {} {}'.format(os.path.join(dest, fname),
                                      os.path.join(HERE, fname)))


def diffconf(*names):
    "compare named configuration files"
    for conf in names:
        _diffconf(conf.strip())


def diffconfg(*names):
    "compare named configuration files + show results in gui"
    for conf in names:
        _diffconf(conf.strip(), gui=True)


def listconfs():
    "list available configs"
    text = "Available Nginx configs: " + ', '.join(sorted(intconf.keys()))
    print(text)
    text = "Available non-Nginx confs: " + ", ".join(sorted(extconf.keys()))
    print(text)


def stop_nginx():
    "stop nginx"
    local('sudo {}/nginx stop'.format(INIT))


def start_nginx():
    "start nginx"
    local('sudo {}/nginx start'.format(INIT))


def restart_nginx():
    "restart nginx"
    local('sudo killall -HUP nginx')


def start_ftp():
    "start vsftpd"
    local('sudo start vsftpd')


def stop_ftp():
    "stop vsftpd"
    local('sudo stop vsftpd')


def restart_ftp():
    "restart vsftpd"
    local('sudo restart vsftpd')


def stop_php():
    "stop php"
    local('sudo {}/php7.0-fpm stop'.format(INIT))


def start_php():
    "start php"
    local('sudo {}/php7.0-fpm start'.format(INIT))


def restart_php():
    "restart php"
    local('sudo {}/php7.0-fpm restart'.format(INIT))


def _report_result(proj, result):
    """get output of start_server command and save to file(s)
    """
    with open('/tmp/server-{}-ok'.format(proj), 'w') as _o:
        print(result.stdout, file=_o)
    with open('/tmp/server-{}-err'.format(proj), 'w') as _o:
        print(result.stderr, file=_o)


def stop_hgweb():
    "stop local Mercurial web server"
    local('sudo kill `cat {}`'.format(hgweb_pid))


def start_hgweb():
    "start local Mercurial web server using hgweb.fcgi"
    start = os.path.join(HGWEB, 'hgweb.fcgi')
    result = local('sudo spawn-fcgi -f {} -s {} -P {} -u {}'.format(start,
                                                                    hgweb_sock,
                                                                    hgweb_pid,
                                                                    'www-data'),
                   capture=True)
    _report_result('hgweb', result)
    #gunicorn3 kan mercurial niet importeren; gunicorn2 slaat vast, als ik het niet als daemon
    # uitvoer zie ik
    #Traceback (most recent call last):
    #File "/usr/lib/python2.7/dist-packages/gunicorn/workers/sync.py", line 130, in handle
    #    self.handle_request(listener, req, client, addr)
    #File "/usr/lib/python2.7/dist-packages/gunicorn/workers/sync.py", line 176, in handle_request
    #    for item in respiter:
    #TypeError: 'hgwebdir' object is not iterable
    ## "start local Mercurial web server using gunicorn for Python 3"
    ## with lcd(HGWEB):
        ## local('sudo /usr/bin/gunicorn -D -b unix:{} -p {} '
              ## 'hgwebwsgi:application'.format(hgweb_sock, hgweb_pid))


def restart_hgweb():
    "restart local Mercurial web server"
    stop_hgweb()
    start_hgweb()


def stop_trac():
    "stop local trac server"
    local('sudo kill `cat {}`'.format(trac_pid))


def start_trac():  # Note: uses gunicorn for Python 2 (2017-10: still needs to)
    "start local trac server"
    with lcd(TRAC):
        result = local('sudo /usr/bin/gunicorn -D -b unix:{} -p {} '
                       'tracwsgi:application'.format(trac_sock, trac_pid), capture=True)
        _report_result('trac', result)


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
    if not project:
        project = django_project_path.keys()
    for proj in project:
        django_pid = _get_django_args(proj)[0]
        if os.path.exists(django_pid):
            local('sudo kill `cat {}`'.format(django_pid))
            local('sudo rm -f {}'.format(django_pid))


def start_django(*project):
    """start indicated Django server(s) using manage.py over fastcgi (python 2 - see
    version history) or using Gunicorn (python 3)
    """
    if not project:
        project = sorted(django_project_path.keys())
    for proj in project:
        pid, sock, path = _get_django_args(proj)
        with lcd(path):
            result = local('sudo /usr/bin/gunicorn3 -D -b unix:{} -p {} '
                           '{}.wsgi:application'.format(sock, pid, proj), capture=True)
            _report_result(proj, result)


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


def _fix_media_prefix(path):

    find = 'ADMIN_MEDIA_PREFIX'
    prefix = "'/static/admin/'"
    settingsfile = os.path.join(path, 'settings.py')
    modified = True
    with open(settingsfile) as _in:
        buf = _in.read()
    if find in buf:
        test = buf.split(find, 1)
        if len(test) > 1:
            head = test[0].rstrip().rstrip('#').rstrip()  # uncomment if necessary
            test = test[1].lstrip().lstrip('=').lstrip(' ')
            if test.startswith(os.linesep):
                tail = test
            else:
                if test.startswith(prefix):
                    tail = test[len(prefix):]
                else:
                    tail = os.linesep + test
        else:
            head = test[0]
            tail = os.linesep
    else:
        head = buf.rstrip()
        tail = os.linesep
    if modified:
        shutil.copyfile(settingsfile, settingsfile + '~')
        with open(settingsfile, 'w') as _out:
            _out.write('{}\n{} = {}{}'.format(head, find, prefix, tail))


def django_css(*project):
    "add symlink to admin CSS for Django project"
    if not project:
        project = django_project_path.keys()
    for proj in project:
        pid, sock, path = _get_django_args(project)
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
            os.mkdir(test)
        if not skip:
            with lcd(test):
                local('ln -s /usr/share/pyshared/django/contrib/admin/static/admin')
            _fix_media_prefix(path)


def _get_cherry_parms(project=None):
    allproj = ('rst2html', 'logviewer', 'magiokis-cherry', 'rst2html_mongo')
    if not project:
        return allproj
    origproj = project
    pad = os.path.join(HOME, 'projects', project)
    if project == allproj[2]:
        project = project.split('-')[0]
    elif project == allproj[3]:
        pad = os.path.join(HOME, 'projects', allproj[0])
    conf = '{}.conf'.format(project)
    prog = 'start_{}'.format(project)
    pid = os.path.join(runpath, '{}.pid'.format(project))
    sock = os.path.join(runpath, '{}.sock'.format(project))
    if origproj == allproj[2]:
        pid = os.path.join(runpath, '{}c.pid'.format(project))
        sock = os.path.join(runpath, '{}c.sock'.format(project))
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
        with lcd(pad):
            result = local('sudo /usr/sbin/cherryd3 '
                           '-c {} -d -p {} -i {}'.format(conf, pid, prog), capture=True)
            _report_result(proj, result)


def restart_cherry(*project):
    "restart cherrypy site (arg:project)"
    if project and project[0] == '?':
        text = "Available CherryPy projects: " + ", ".join(_get_cherry_parms())
        print(text)
        return
    if not project:
        project = _get_cherry_parms()
    for proj in project:
        stop_cherry(proj)
        start_cherry(proj)


def check_all_servers(*project):
    "assuming server is started when there is a pid file"
    if not project:
        all_django = list(django_project_path.keys())
        all_cherry = list(_get_cherry_parms())
        all_other = ['trac', 'hgweb']  # , 'plone']
        other_pid = [trac_pid, hgweb_pid]  # , plone_pid]
        project = all_django + all_cherry + all_other
    all_clear = True
    for proj in project:
        if proj in all_django:
            pid = _get_django_args(proj)[0]
        elif proj in all_cherry:
            pid = _get_cherry_parms(proj)[3]
        elif proj in all_other:
            pid = other_pid[all_other.index(proj)]
        if os.path.exists(pid):
            continue
        print("{}: no pid file, starting server probably failed".format(
            proj))
        all_clear = False
    if all_clear:
        print("all local servers ok")


def _get_sitenames():
    """get the names of the local domains from the hosts file
    """
    sites = []
    with open('/etc/hosts') as _in:
        for line in _in:
            if line.startswith('#'):
                continue
            for name in ('lemoncurry', 'magiokis'):
                if name in line:
                    sites.append(line.strip().split()[1])
    return sites


def _check_page(address):
    """call up a specific page to inspect the result
    """
    return requests.get('http://' + address)


def _check_frontpage(sitename):
    """simply call the domain to see what response we get back
    """
    r = _check_page(sitename)
    if sitename.startswith('trac'):
        if r.status_code == 401:  # not authenticated is enough for an answer here
            return 200
    return r.status_code


def _check_sites(quick=True, sites=None):
    """alle locale sites langslopen om te zien of de pagina's werken

    verkorte versie: check alleen de frontpage
    van sommige sites wil je ook zien of vervolgpagina's werken
    vandaar de complete versie:
    van alle locale sites waar een beperkt aantal vervolgpagina's mogelijk is
    al deze mogelijkheden aflopen
    van gelijksoortige pagina's is één variant voldoende
    """
    sitenames = _get_sitenames()
    if sites:
        sitenames = [name for name in sites if name in sitenames]
    for base in sitenames:
        print('checking {}... '.format(base), end='')
        ok = _check_frontpage(base)
        if ok != 200:
            print('error {}'.format(ok))
            continue
        if quick:
            print('ok')
            if base in check_address['quick']:
                test = base + check_address['quick'][base]
                ok = _check_page(test).status_code
                if ok != 200:
                    print('    error {} on {}'.format(ok, test))
        else:
            print('frontpage ok', end='')
            to_check = []
            if base in check_address['full']:
                if not check_address['full'][base]:
                    print(', no further checking necessary')
                    continue
                print()
                to_read = os.path.join('~', 'nginx-config', 'check-pages', check_address['full'][base])
                to_read = os.path.expanduser(to_read)
                if os.path.exists(to_read):
                    with open(to_read) as _in:
                        to_check = [line.strip() for line in _in]
                    for test in to_check:
                        page = '{}{}'.format(base, test)
                        print('checking {}...'.format(page), end=' ')
                        ok = _check_page(page).status_code
                        if ok == 200:
                            print('ok')
                        else:
                            print('error {}'.format(ok))  # test))
                else:
                    print('    check-pages file missing for {}'.format(base))
            else:
                print()
                print('    check_address entry missing for {}'.format(base))


def check_all_sites():
    "quick (frontpage only) check if all local sites are working"
    _check_sites()


def check_all_pages(*args):
    "full check if all local sites are working"
    if not args:
        _check_sites(quick=False)
    else:
        _check_sites(quick=False, sites=[x for x in args])


def _plone(action, *sitenames):
    def _doit(sitename, action):
        plonedir = os.path.join(HOME, '{}/zinstance'.format(sitename.title()))
        with lcd(plonedir):
            if action == 'start':
                result = local('bin/plonectl start', capture=True)
                _report_result("plone", result)
            elif action == 'stop':
                local('bin/plonectl stop')
            elif action == 'buildout':
                local('bin/buildout')
    if not sitenames:
        sitenames = PLONES
    for name in sitenames:
        _doit(name, action)


def start_plone(*sitenames):
    "start Plone default instance"
    _plone('start', *sitenames)


def stop_plone(*sitenames):
    "stop Plone default instance"
    _plone('stop', *sitenames)


def restart_plone(*sitenames):
    "restart Plone default instance"
    stop_plone(*sitenames)
    start_plone(*sitenames)


def buildout_plone(*sitenames):
    """run buildout on Plone instance

    to be used in this combo:
        fabsrv modconf:plone-buildout buildout_plone restart_plone
    """
    _plone('buildout', *sitenames)


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
        newname = os.path.join(A_ENABL, conf)
        local(' sudo rm {}'.format(newname))


def edit(name):
    "edit a file related to the server configuration"
    local("SciTE {} &".format(os.path.join(HERE, name)))


def stop_gunicorn():
    "stop local gunicorn server"
    local('sudo kill `cat {}`'.format(guni_pid))


def start_gunicorn():
    "start local gunicorn server+app"
    ## auth = '{},{},{}'.format(gproject, os.path.join(GUNI, 'trac_users'), gproject)
    with lcd('~/www/gunicorn'):
        local('sudo gunicorn -D -b 127.0.0.1:9100 -p {} myapp:app'.format(guni_pid))


def restart_gunicorn():
    "restart local gunicorn server"
    stop_gunicorn()
    start_gunicorn()


def _start_all_servers():
    """try to start all wsgi servers
    output is gathered in /tmp/server-{}-ok and -err. It should be discernible which one fails
    and as such from where we need to try again
    """
    # all_django = sorted(django_project_path_keys())
    # all_cherry = _get_cherry_parms()
    # if os.path.exists('/tmp/server-trac-err'):
    #     # check if something went wrong, otherwise:
    #     for name in glob.glob('/tmp/server-*-*'):
    #         os.remove(name)
    # elif os.path.exists('/tmp/server-hgweb-err'):
    #     names = names[-4:]
    # elif os.path.exists('/tmp/server-{}-err'.format(all_django[-1])):
    #     names = names[-3:]
    # elif os.path.exists('/tmp/server-{}-mongo-err'.format(all_cherry[-1])):
    #     names = names[-2:]
    # elif os.path.exists('/tmp/server-plone-err'):
    #     names = names[-1:]


def _serve(names, **kwargs):
    """manage all server managers
    """
    stop_server = 'stop' in kwargs
    start_server = 'start' in kwargs
    if start_server and not names:
        _start_all_servers()
        return
    funcs = {'django': (start_django, stop_django, ''),
             'cherry': (start_cherry, stop_cherry, ''),
             'plone': (start_plone, stop_plone, ''),
             'trac': (start_trac, stop_trac, ''),
             'hgweb': (start_hgweb, stop_hgweb, ''),
             'apache': (start_apache, stop_apache, restart_apache),
             'nginx': (start_nginx, stop_nginx, restart_nginx),
             'php': (start_php, stop_php, restart_php),
             'ftp': (start_ftp, stop_ftp, restart_ftp)}
    for name in names:
        if name in funcs:
            start, stop, restart = funcs[name]
            if stop_server and start_server and restart:
                restart()
                return
            if stop_server:
                stop()
            if start_server:
                start()
        elif name in django_sites:
            if stop_server:
                stop_django(name)
            if start_server:
                start_django(name)
        elif name in _get_cherry_parms():
            if stop_server:
                stop_cherry(name)
            if start_server:
                start_cherry(name)
        elif name in PLONES:
            if stop_server:
                stop_plone(name)
            if start_server:
                start_plone(name)


def stop_server(*names):
    "stop local server"
    _serve(names, stop=True)


def start_server(*names):
    "start local server"
    _serve(names, start=True)


def restart_server(*names):
    "restart local server"
    _serve(names, stop=True, start=True)


def list_servers():
    "list of django and cherrypy server names"
    ## print('er zijn nog verschillen:')
    ## print(sorted(intconf['django']))
    ## print(sorted(django_project_path.keys()))
    ## print(sorted(intconf['cherrypy']))
    ## print(sorted(x for x in _get_cherry_parms()))
    server_list = django_project_path.keys() + [x for x in _get_cherry_parms()]
    print("list of django and cherrypy server names:", ', '.join(server_list))


def list_domains(*args):
    "list of virtual domains per Nginx configuration"
    allconfs = intconf.keys()
    if not args:
        args = allconfs

    for conf in args:
        try:
            sites = intconf[conf]
        except KeyError:
            print('unknown config')
        else:
            print("domains for config {}: {}".format(conf, ', '.join(sites)))
