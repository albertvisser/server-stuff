"""INVoke commands for (Nginx) server configs
"""
import os
from invoke import task
from config import AVAIL, ENABL, HERE, EDITORCMD, intconf, extconf
import tasks_shared as shared

FROM = os.path.join(HERE, 'nginx')


def _diffconf(c, name, gui=False):
    "compare a configuration file"
    if name in extconf:
        dest, _, fname = extconf[name]
        if fname.startswith('@'):
            fname = name + fname[1:]
    else:
        dest, fname = AVAIL, name
    old, new = os.path.join(dest, fname), os.path.join(FROM, fname)
    cmd = 'meld' if gui else 'diff -s'
    c.run(f'{cmd} {old} {new}')


@task(help={'names': 'comma-separated list of filenames'})
def addconf(c, names):
    """enable Nginx configuration for one or more (file) names
    provided as a comma separated string"""
    for conf in names.split(','):
        shared.add_conf(c, conf.strip(), AVAIL, ENABL)


@task(help={'names': 'comma-separated list of filenames'})
def rmconf(c, names):
    "disable Nginx configuration for one or more file names"
    for conf in names.split(','):
        shared.remove_conf(c, conf.strip(), ENABL)


@task(help={'names': 'comma-separated list of filenames'})
def modconf(c, names):
    "deploy modifications for Nginx configuration file(s); replace version"
    for conf in names.split(','):
        shared.mod_conf(c, os.path.join(FROM, conf.strip()), AVAIL)


@task(help={'names': 'comma-separated list of filenames'})
def modconfb(c, names):
    "modconf: backup & replace version"
    for conf in names.split(','):
        shared.mod_conf(c, os.path.join(FROM, conf.strip()), AVAIL, backup=True)


@task(help={'names': 'comma-separated list of filenames'})
def modconfa(c, names):
    "modconf: backup & append version"
    for conf in names.split(','):
        shared.mod_conf(c, os.path.join(FROM, conf.strip()), AVAIL, append=True)


@task(help={'names': 'comma-separated list of filenames'})
def newconf(c, names):
    """shortcut to define and enable a new Nginx config in one go
    """
    for conf in names.split(','):
        shared.mod_conf(c, os.path.join(FROM, conf.strip()), AVAIL)
        shared.add_conf(c, conf.strip(), AVAIL, ENABL)


@task(help={'names': 'comma-separated list of filenames'})
def diffconf(c, names=None):
    "compare named configuration files"
    if not names:
        c.run(f'diff -s {FROM} {AVAIL}')
        return
    for conf in names.split(','):
        _diffconf(c, conf.strip())


@task(help={'names': 'comma-separated list of filenames'})
def diffconfg(c, names=None):
    "compare named configuration files + show results in gui"
    if not names:
        c.run(f'meld {FROM} {AVAIL}')
        return
    for conf in names.split(','):
        _diffconf(c, conf.strip(), gui=True)


@task
def list(c):
    "list available configs"
    text = "Available Nginx configs: " + ', '.join(sorted(intconf.keys()))
    print(text)
    text = "Available non-Nginx confs: " + ", ".join(sorted(extconf.keys()))
    print(text)


@task(help={'name': 'name of file to edit'})
def editconf(c, name):
    "edit a file related to the server configuration"
    # c.run("SciTE {} &".format(os.path.join(FROM, name)))
    c.run(EDITORCMD.format(os.path.join(FROM, name)))


@task(help={'names': 'comma-separated list of filenames'})
def list_domains(c, names=None):
    "list of virtual domains per Nginx configuration"
    allconfs = intconf.keys()
    names = names.split(',') if names else allconfs

    for conf in names:
        if conf in allconfs:
            sites = ', '.join(intconf[conf])
            print(f'domains for config "{conf}": {sites}')
        else:
            print(f'unknown config "{conf}"')


@task
def stop(c):
    "stop nginx"
    # c.run('sudo {}/nginx stop'.format(INIT))
    c.run('sudo systemctl stop nginx.service')


@task
def start(c):
    "start nginx"
    # c.run('sudo {}/nginx start'.format(INIT))
    c.run('sudo systemctl start nginx.service')


@task
def restart(c):
    "restart nginx"
    # c.run('sudo killall -HUP nginx')
    c.run('sudo systemctl restart nginx.service')
