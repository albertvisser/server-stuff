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
import tasks_gitweb
import tasks_django
import tasks_cherrypy
import tasks_plone
import tasks_sites
import tasks_shared as shared

all_django = sorted(tasks_django.get_projectnames())
all_cherry = sorted(tasks_cherrypy.get_projectnames())
all_servers = ['plone'] + all_django + list(all_cherry) + ['trac', 'hgweb']
all_other = ['trac', 'hgweb']  # , 'plone']

@task(help={'name': 'name of the new init file'})
def addstartup(c, name):
    """add an init file to the system startup sequence

    don't forget to register in the extconf dict with INIT as destination
    """
    c.run('sudo chmod +x {}/{}'.format(INIT, name))     # make sure it's executable
    c.run('sudo update-rc.d {} defaults'.format(name))  # add to defaults


def get_parms(name):
    "get extconf dictionary for parameters to use"
    if name in extconf:
        dest, needs_sudo, fname = extconf[name]
        fname = fname.replace('@', name)
        frompath = os.path.join(HERE, 'misc')
    else:
        raise ValueError('Unknown config `{}`'.format(name))
    return os.path.join(frompath, fname), dest, needs_sudo


@task(help={'names': 'comma-separated list of filenames'})
def editconf(c, names):
    "edit a file related to a configuration"
    names = names.split(',') if names else []
    for conf in names:
        path = get_parms(conf)[0]
        # c.run("SciTE {} &".format(path))
        c.run(EDITORCMD.format(path))

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


def _diffconf(c, gui=False):
    "compare configuration files"
    locs = {}
    for key, stuff in extconf.items():
        path, _, fname = stuff
        fname = fname.replace('@', key)
        if os.path.exists(os.path.join(path, fname)):
            locs[fname] = path
        else:
            print('comparing {} skipped: does not exist in {}'.format(fname, path))
    path = os.path.join(HERE, 'misc')
    for fname in os.listdir(path):
        if fname in locs:
            if gui:
                c.run('meld {} {}'.format(os.path.join(path, fname),
                                          os.path.join(locs[fname], fname)))
            else:
                result = c.run('diff -s {} {}'.format(os.path.join(path, fname),
                                          os.path.join(locs[fname], fname)),
                               hide=True, warn=True)
                # print(result.command)
                if result.exited:
                    outname = '/tmp/diff-{}'.format(fname)
                    print('differences for {}, see {}'.format(fname, outname))
                    with open(outname, 'w') as f:
                        print(result.stdout, file=f)
                else:
                    print(result.stdout, end='')
            # shared.do_compare(os.path.join(path, fname), os.path.join(locs[fname], fname))


@task
def compare(c):
    "compare all configuration files that can be changed from here"
    _diffconf(c)


@task
def compareg(c):
    "compare all configuration files that can be changed from here, in gui"
    _diffconf(c, gui=True)


@task(help={'project': 'comma-separated list of server names'})
def check_all(c, project=''):
    "assuming server is started when there is a pid file"
    other_pid = dict(zip(all_other, [tasks_trac.trac_pid, tasks_hgweb.hgweb_pid]))  # , plone_pid]
    if not project:
        project = all_django + all_cherry + all_other
    else:
        project = project.split(',')
    all_clear = True
    for proj in project:
        if proj in all_django:
            pid = tasks_django.get_pid(proj)
        elif proj in all_cherry:
            pid = tasks_cherrypy.get_pid(proj)
        elif proj in other_pid:
            pid = other_pid[proj]
        else:
            continue
        if os.path.exists(pid):
            print("{}: found pid file, server probably started".format(proj))
            continue
        print("{}: no pid file, starting server probably failed".format(proj))
        all_clear = False
    if all_clear:
        print("all local servers ok")


def _start_all(c):
    """try to start all wsgi servers
    output is gathered in /tmp/server-{}-ok and -err. It should be discernible which one fails
    and as such from where we need to try again
    """
    started = os.path.exists('/tmp/server-{}-err'.format(all_servers[0]))
    for ix, name in enumerate(all_servers):
        if os.path.exists('/tmp/server-{}-err'.format(name)):
            if ix == 0:
                started = True
            previous = name
            continue
        if ix > 1 and started:
            print('restarting from {}'.format(previous))
            restart(c, previous)
        print('starting server {}'.format(name))
        start(c, name)


def _serve(c, names, **kwargs):
    """manage all server managers with one command
    """
    stop_server = 'stop' in kwargs
    start_server = 'start' in kwargs
    if start_server and not names:
        _start_all(c)
        return
    mnames = {'django': tasks_django, 'cherry': tasks_cherrypy, 'plone': tasks_plone,
              'trac': tasks_trac, 'hgweb': tasks_hgweb, 'apache': tasks_apache,
              'nginx': tasks_nginx, 'php': tasks_php, 'ftp': tasks_ftp}
    if not names:
        names = ['plone', 'django', 'cherry', 'trac', 'hgweb']
    else:
        names = names.split(',')
    for name in names:
        if name in mnames:
            if stop_server and start_server and restart:
                mnames[name].restart(c)
                return
            if stop_server:
                mnames[name].stop(c)
            if start_server:
                mnames[name].start(c)
        elif name in all_django:
            if stop_server:
                mnames['django'].stop(c, name)
            if start_server:
                mnames['django'].start(c, name)
        elif name in all_cherry:
            if stop_server:
                mnames['cherry'].stop(c, name)
            if start_server:
                mnames['cherry'].start(c, name)
        elif name in PLONES:
            if stop_server:
                mnames['plone'].stop(c, name)
            if start_server:
                mnames['plone'].start(c, name)
        # else:  # geen andere mogelijkheden als wat al in mnames zit
        #     if stop_server:
        #         mnames[name].stop(c)
        #     if start_server:
        #         mnames[name].start(c)


@task(help={'names': 'comma-separated list of filenames'})
def stop(c, names=None):
    "stop local server"
    _serve(c, names, stop=True)


@task(help={'names': 'comma-separated list of filenames'})
def start(c, names=None):
    "start local server"
    print(names)
    _serve(c, names, start=True)


@task(help={'names': 'comma-separated list of filenames'})
def restart(c, names=None):
    "restart local server"
    _serve(c, names, stop=True, start=True)


ns = Collection()
ns.add_collection(tasks_nginx, name='nginx')
ns.add_collection(tasks_ftp, name='ftp')
ns.add_collection(tasks_php, name='php')
ns.add_collection(tasks_apache, name='apache')
ns.add_collection(tasks_trac, name='trac')
ns.add_collection(tasks_hgweb, name='hgweb')
ns.add_collection(tasks_gitweb, name='gitweb')
ns.add_collection(tasks_django, name='django')
ns.add_collection(tasks_cherrypy, name='cherrypy')
ns.add_collection(tasks_plone, name='plone')
ns.add_collection(tasks_sites, name='sites')
ns.add_task(addstartup)
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
