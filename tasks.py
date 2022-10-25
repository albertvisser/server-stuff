"""General tasks that can be INVOKEd

also creates namespaces from other tasks files
"""
import os
from config import INIT, PLONES, HERE, EDITORCMD, extconf
from invoke import task, Collection
import tasks_nginx
import tasks_ftp
import tasks_php
import tasks_apache
import tasks_trac
import tasks_hgweb
import tasks_django
import tasks_cherrypy
import tasks_plone
import tasks_sites
import tasks_shared as shared

all_django = sorted(tasks_django.get_projectnames())
all_cherry = sorted(tasks_cherrypy.get_projectnames())
all_rst2html = [x for x in all_cherry if x.startswith('rst2html')]
all_other = ['trac', 'hgweb']
all_servers = ['plone'] + all_django + list(all_cherry)  # + all_other
all_names = {'django': tasks_django, 'cherrypy': tasks_cherrypy, 'plone': tasks_plone,
             'trac': tasks_trac, 'hgweb': tasks_hgweb, 'apache': tasks_apache,
             'nginx': tasks_nginx, 'php': tasks_php, 'ftp': tasks_ftp}


@task(help={'name': 'name of the new init file'})
def addstartup(c, name):
    """add an init file to the system startup sequence

    don't forget to register in the extconf dict with INIT as destination
    """
    c.run(f'sudo chmod +x {INIT}/{name}')     # make sure it's executable
    c.run(f'sudo update-rc.d {name} defaults')  # add to defaults


@task(help={'names': 'comma-separated list of filenames'})
def editconf(c, names):
    "edit a file related to a configuration"
    names = names.split(',') if names else []
    for conf in names:
        path = get_parms(conf)[0]
        # c.run("SciTE {} &".format(path))
        c.run(EDITORCMD.format(path))


@task
def listconf(c):
    """list "other" configuration files"""
    print('deployable non-webserver configuration files:')
    for name, data in sorted(extconf.items()):
        path, needs_sudo, filename = data
        print(': '.join((name, os.path.join(path, filename.replace('@', name)))))


@task(help={'names': 'comma-separated list of filenames'})
def modconf(c, names=None):
    "deploy modifications for configuration file(s); replace version"
    names = names.split(',') if names else []
    for conf in names:
        path, dest, sudo = get_parms(conf)
        shared.mod_conf(c, path, dest, needs_sudo=sudo)


@task(help={'names': 'comma-separated list of filenames'})
def modconfb(c, names=None):
    "modconf: backup & replace version"
    names = names.split(',') if names else []
    for conf in names:
        path, dest, sudo = get_parms(conf)
        shared.mod_conf(c, path, dest, needs_sudo=sudo, backup=True)


@task(help={'names': 'comma-separated list of filenames'})
def modconfa(c, names=None):
    "modconf: backup & append version"
    names = names.split(',') if names else []
    for conf in names:
        path, dest, sudo = get_parms(conf)
        shared.mod_conf(c, path, dest, needs_sudo=sudo, append=True)


def get_parms(name):
    "get extconf dictionary for parameters to use"
    if name in extconf:
        dest, needs_sudo, fname = extconf[name]
        fname = fname.replace('@', name)
        frompath = os.path.join(HERE, 'misc')
    else:
        raise ValueError(f'Unknown config `{name}`')
    return os.path.join(frompath, fname), dest, needs_sudo


@task
def compare(c):
    "compare all configuration files that can be changed from here"
    _diffconf(c)


@task
def compareg(c):
    "compare all configuration files that can be changed from here, in gui"
    _diffconf(c, gui=True)


def _diffconf(c, gui=False):
    "compare configuration files"
    locs = {}
    for key, stuff in extconf.items():
        path, _, fname = stuff
        fname = fname.replace('@', key)
        if os.path.exists(os.path.join(path, fname)):
            locs[fname] = path
        else:
            print(f'comparing {fname} skipped: does not exist in {path}')
    path = os.path.join(HERE, 'misc')
    for fname in os.listdir(path):
        if fname in locs:
            old, new = os.path.join(path, fname), os.path.join(locs[fname], fname)
            if gui:
                c.run(f'meld {old} {new}')
            else:
                result = c.run(f'diff -s {old} {new}', hide=True, warn=True)
                # print(result.command)
                if result.exited:
                    outname = f'/tmp/diff-{fname}'
                    print(f'differences for {fname}, see {outname}')
                    with open(outname, 'w') as f:
                        print(result.stdout, file=f)
                else:
                    print(result.stdout, end='')
            # shared.do_compare(os.path.join(path, fname), os.path.join(locs[fname], fname))


@task(help={'names': 'comma-separated list of server names'})
def check_all(c, names=''):
    "assuming server is started when there is a pid file"
    other_pid = dict(zip(all_other, [tasks_trac.trac_pid, tasks_hgweb.hgweb_pid]))  # , plone_pid]
    if not names:
        names = all_django + all_cherry + all_other
    else:
        names = names.split(',')
    all_clear = True
    for proj in names:
        if proj in all_django:
            pid = tasks_django.get_pid(proj)
        elif proj in all_cherry:
            pid = tasks_cherrypy.get_pid(proj)
        elif proj in other_pid:
            pid = other_pid[proj]
        else:
            continue
        if os.path.exists(pid):
            print(f"{proj}: found pid file, server probably started")
            continue
        print(f"{proj}: no pid file, server not started or starting failed")
        all_clear = False
    if all_clear:
        print("all local servers ok")


@task(help={'names': 'comma-separated list of filenames'})
def stop(c, names=None):
    "stop local server"
    _serve(c, names, stop=True)


@task(help={'names': 'comma-separated list of filenames'})
def start(c, names=None):
    "start local server"
    _serve(c, names, start=True)


@task(help={'names': 'comma-separated list of filenames'})
def restart(c, names=None):
    "restart local server"
    _serve(c, names, stop=True, start=True)


def _serve(c, names, **kwargs):
    """manage all server managers with one command
    """
    stop_server = 'stop' in kwargs
    start_server = 'start' in kwargs
    if start_server and not names:
        _start_all(c)
        return
    if not names:
        names = ['plone', 'django', 'cherrypy']  # , 'trac', 'hgweb']
    else:
        names = names.split(',')
    for name in names:
        if name in all_names:
            if name == 'django':
                for name in all_django:
                    _serve_django(c, name, stop_server, start_server)
            elif name == 'cherrypy':
                for name in all_cherry:
                    _serve_cherry(c, name, stop_server, start_server)
            elif name == 'plone':
                for name in PLONES:
                    _serve_plone(c, name, stop_server, start_server)
            elif stop_server and start_server and restart:
                # tijdelijk (?) om te zien of dit gebruikt wordt
                print('attention: restarting via _serve')
                all_names[name].restart(c)
                return
        elif name in all_django:
            _serve_django(c, name, stop_server, start_server)
        elif name in all_cherry:
            _serve_cherry(c, name, stop_server, start_server)
        elif name in PLONES:
            _serve_plone(c, name, stop_server, start_server)
        elif name == 'rst2html':
            for name in all_rst2html:
                _serve_cherry(c, name, stop_server, start_server)
        else:
            print('unknown server name')


def _start_all(c):
    """try to start all wsgi servers
    output is gathered in /tmp/server-{}-ok and -err. It should be discernible which one fails
    and as such from where we need to try again
    """
    # FIXME: of dit werkt is maar de vraag omdat zowel het err als het ok file aangemaakt worden
    started = os.path.exists(f'/tmp/server-{all_servers[0]}-err')
    for ix, name in enumerate(all_servers):
        if os.path.exists(f'/tmp/server-{name}-err'):
            if ix == 0:
                started = True
            previous = name
            continue
        if ix > 0 and started:
            print(f'restarting from {previous}')
            restart(c, previous)
            started = False
        print(f'starting server {name}')
        start(c, name)


def _serve_django(c, name, stop_server, start_server):
    "start/stop django wsgi server"
    start_stop(c, name, stop_server, start_server, 'django')


def _serve_cherry(c, name, stop_server, start_server):
    "start/stop cherrypy wsgi server"
    start_stop(c, name, stop_server, start_server, 'cherrypy')


def _serve_plone(c, name, stop_server, start_server):
    "start/stop Plone instance"
    start_stop(c, name, stop_server, start_server, 'plone')


def start_stop(c, name, stop_server, start_server, typename):
    "check flags to determine what to do"
    if stop_server:
        all_names[typename].stop(c, name)
    if start_server:
        all_names[typename].start(c, name)


ns = Collection()
ns.add_collection(tasks_nginx, name='nginx')
ns.add_collection(tasks_ftp, name='ftp')
ns.add_collection(tasks_php, name='php')
ns.add_collection(tasks_apache, name='apache')
ns.add_collection(tasks_trac, name='trac')
ns.add_collection(tasks_hgweb, name='hgweb')
ns.add_collection(tasks_django, name='django')
ns.add_collection(tasks_cherrypy, name='cherrypy')
ns.add_collection(tasks_plone, name='plone')
ns.add_collection(tasks_sites, name='sites')
ns.add_task(addstartup)
ns.add_task(listconf)
ns.add_task(editconf)
ns.add_task(modconf)
ns.add_task(modconfa)
ns.add_task(modconfb)
ns.add_task(compare)
ns.add_task(compareg)
server = Collection('server')
server.add_task(check_all)
server.add_task(stop)
server.add_task(start)
server.add_task(restart)
ns.add_collection(server)
