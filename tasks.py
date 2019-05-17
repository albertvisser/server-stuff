import os
import shutil
import datetime
import requests
from config import INIT
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
from all_local_pages import check_address

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
    if name in extconf:
        dest, needs_sudo, fname = extconf[name]
        fname = fname.replace('@', name)
        frompath =  os.path.join(HERE, 'misc')
    return os.path.join(frompath, fname), dest, needs_sudo

@task(help={'names': 'comma-separated list of filenames'})
def modconf(c, names=None):
    "deploy modifications for configuration file(s); replace version"
    names = names.split(',') if names else []
    for conf in names:
        path, dest, sudo = get_parms(name)
        shared.mod_conf(c, path, dest, needs_sudo=sudo)


@task(help={'names': 'comma-separated list of filenames'})
def modconfb(c, names=None):
    "modconf: backup & replace version"
    names = names.split(',') if names else []
    for conf in names:
        path, dest, sudo = get_parms(name)
        shared.mod_conf(c, path, dest, needs_sudo=sudo, backup=True)


@task(help={'names': 'comma-separated list of filenames'})
def modconfa(c, names=None):
    "modconf: backup & append version"
    names = names.split(',') if names else []
    for conf in names:
        path, dest, sudo = get_parms(name)
        shared.mod_conf(c, path, dest, needs_sudo=sudo, append=True)


@task(help={'project': 'comma-separated list of server names'})
def check_all(c, project=''):
    "assuming server is started when there is a pid file"
    other_pid = dict(zip(all_other,[tasks_trac.trac_pid, tasks_hgweb.hgweb_pid]))  # , plone_pid]
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
ns.add_collection(tasks_django, name='django')
ns.add_collection(tasks_cherrypy, name='cherrypy')
ns.add_collection(tasks_plone, name='plone')
ns.add_collection(tasks_sites, name='sites')
ns.add_task(addstartup)
ns.add_task(modconf)
ns.add_task(modconfa)
ns.add_task(modconfb)
server = Collection('server')
server.add_task(check_all)
server.add_task(stop)
server.add_task(start)
server.add_task(restart)
ns.add_collection(server)
