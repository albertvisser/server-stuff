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
def addconf(c, names=None):
    """enable Nginx configuration for one or more (file) names
    provided as a comma separated string"""
    names = names.split(',') if names else []
    for conf in names:
        shared.add_conf(c, conf.strip(), AVAIL, ENABL)


@task(help={'names': 'comma-separated list of filenames'})
def rmconf(c, names=None):
    "disable Nginx configuration for one or more file names"
    names = names.split(',') if names else []
    for conf in names:
        shared.remove_conf(c, conf.strip(), ENABL)


@task(help={'names': 'comma-separated list of filenames'})
def modconf(c, names=None):
    "deploy modifications for Nginx configuration file(s); replace version"
    names = names.split(',') if names else []
    for conf in names:
        shared.mod_conf(c, os.path.join(FROM, conf.strip()), AVAIL)


@task(help={'names': 'comma-separated list of filenames'})
def modconfb(c, names=None):
    "modconf: backup & replace version"
    names = names.split(',') if names else []
    for conf in names:
        shared.mod_conf(c, os.path.join(FROM, conf.strip()), AVAIL, backup=True)


@task(help={'names': 'comma-separated list of filenames'})
def modconfa(c, names=None):
    "modconf: backup & append version"
    names = names.split(',') if names else []
    for conf in names:
        shared.mod_conf(c, os.path.join(FROM, conf.strip()), AVAIL, append=True)


@task(help={'names': 'comma-separated list of filenames'})
def newconf(c, names=None):
    """shortcut to define and enable a new Nginx config in one go
    """
    names = names.split(',') if names else []
    for conf in names:
        shared.mod_conf(c, os.path.join(FROM, conf.strip()), AVAIL)
        shared.add_conf(c, conf.strip(), AVAIL, ENABL)


@task(help={'names': 'comma-separated list of filenames'})
def diffconf(c, names=None):
    "compare named configuration files"
    names = names.split(',') if names else []
    for conf in names:
        _diffconf(c, conf.strip())


@task(help={'names': 'comma-separated list of filenames'})
def diffconfg(c, names=None):
    "compare named configuration files + show results in gui"
    names = names.split(',') if names else []
    for conf in names:
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


@task
def compare(c):
    "compare all nginx configurations that can be changed from here"
    c.run(f'diff -s {FROM} {AVAIL}')


@task
def compareg(c):
    "compare all nginx configurations that can be changed from here, in gui"
    c.run(f'meld {FROM} {AVAIL}')
