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
servertypes = {'django': {'names': all_django, 'handler': tasks_django},
               'cherrypy': {'names': list(all_cherry), 'handler': tasks_cherrypy},
               'rst2html': {'names': all_rst2html, 'handler': tasks_cherrypy},
               # 'plone': {'names': PLONES, 'handler': tasks_plone},
               'trac': {'names': ['trac'], 'handler': tasks_trac},
               # 'hgweb': {'names': ['hgweb'], 'handler': tasks_hgweb}
               }


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
    _serve(c, names, stop_server=True)


@task(help={'names': 'comma-separated list of filenames'})
def start(c, names=None):
    "start local server"
    _serve(c, names, start_server=True)


@task(help={'names': 'comma-separated list of filenames'})
def restart(c, names=None):
    "restart local server"
    _serve(c, names, stop_server=True, start_server=True)


def _serve(c, names, stop_server=False, start_server=False):
    """manage all server managers with one command
    """
    if not names:
        names = list(servertypes)
        names.remove('rst2html')  # remove duplicates
    else:
        names = names.split(',')
    for name in names:
        typename, is_group = determine_servertype(name)
        if not typename:
            print(f'unknown server name `{name}`')
            continue
        if is_group:
            for servername in servertypes[typename]['names']:
                start_stop(c, servername, stop_server, start_server, typename)
        else:
            start_stop(c, name, stop_server, start_server, typename)


def determine_servertype(name):
    "Find type of server and if you want the group or a specific one"
    is_group = True
    if name in servertypes:
        return name, is_group
    is_group = False
    for typename, data in servertypes.items():
        if name in data['names']:
            return typename, is_group
    return '', is_group


def start_stop(c, name, stop_server, start_server, typename):
    "check flags to determine what to do"
    name_needed = len(servertypes[typename]['names']) > 1
    if stop_server:
        if name_needed:
            all_names[typename].stop(c, name)
        else:
            all_names[typename].stop(c)
    if start_server:
        if name_needed:
            all_names[typename].start(c, name)
        else:
            all_names[typename].start(c)


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
