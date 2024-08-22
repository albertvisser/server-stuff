"""INVoke commands related to apache server configs
"""
import os.path
from invoke import task
from config import INIT, HERE, A_AVAIL, A_ENABL, EDITORCMD, extconf
import tasks_shared as shared
FROM = os.path.join(HERE, 'apache')


@task
def stop(c):
    "stop apache"
    c.run(f'sudo {INIT}/apache2 stop')


@task
def start(c):
    "start apache"
    c.run(f'sudo {INIT}/apache2 start')


@task
def restart(c):
    "restart apache"
    c.run(f'sudo {INIT}/apache2 restart')


@task(help={'names': 'comma-separated list of filenames'})
def addconf(c, names):
    """enable Apache configuration for one or more (file) names
    provided as a comma separated string"""
    for conf in names.split(','):
        shared.add_conf(c, conf, A_AVAIL, A_ENABL)


@task(help={'name': 'name of file to edit'})
def editconf(c, name):
    "edit a file related to the server configuration"
    # c.run("SciTE {} &".format(os.path.join(FROM, name)))
    c.run(EDITORCMD.format(os.path.join(FROM, name)))


@task(help={'names': 'comma-separated list of filenames'})
def modconf(c, names):
    "deploy modifications for Apache configuration file(s), replace version"
    for conf in names.split(','):
        shared.mod_conf(c, os.path.join(FROM, conf), A_AVAIL)


@task(help={'names': 'comma-separated list of filenames'})
def modconfb(c, names):
    "modconf with backup"
    for conf in names.split(','):
        shared.mod_conf(c, os.path.join(FROM, conf), A_AVAIL, backup=True)


@task(help={'names': 'comma-separated list of filenames'})
def modconfa(c, names):
    "modconf with append (and backup)"
    for conf in names.split(','):
        shared.mod_conf(c, os.path.join(FROM, conf), A_AVAIL, append=True)


@task(help={'names': 'comma-separated list of filenames'})
def rmconf(c, names):
    "disable Apache configuration for one or more file names"
    for conf in names.split(','):
        shared.remove_conf(c, conf, A_ENABL)


@task(help={'names': 'comma-separated list of filenames'})
def diffconf(c, names=None):
    "compare named configuration files"
    if not names:
        c.run(f'diff -s {FROM} {A_AVAIL}')
        return
    for conf in names.split(','):
        _diffconf(c, conf.strip())


@task(help={'names': 'comma-separated list of filenames'})
def diffconfg(c, names=None):
    "compare named configuration files + show results in gui"
    if not names:
        c.run(f'meld {FROM} {A_AVAIL}')
        return
    for conf in names.split(','):
        _diffconf(c, conf.strip(), gui=True)


def _diffconf(c, name, gui=False):
    "compare a configuration file"
    if name in extconf:
        dest, _, fname = extconf[name]
        if fname.startswith('@'):
            fname = name + fname[1:]
    else:
        dest, fname = A_AVAIL, name
    old, new = os.path.join(dest, fname), os.path.join(FROM, fname)
    cmd = 'meld' if gui else 'diff -s'
    c.run(f'{cmd} {old} {new}')
