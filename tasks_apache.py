"""INVoke commands related to apache server configs
"""
import os.path
from invoke import task
from config import INIT, HERE, A_AVAIL, A_ENABL, EDITORCMD
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
def addconf(c, names=None):
    """enable Apache configuration for one or more (file) names
    provided as a comma separated string"""
    if names is None:
        return
    names = names.split(',')
    for conf in names:
        shared.add_conf(c, conf, A_AVAIL, A_ENABL)


@task(help={'name': 'name of file to edit'})
def editconf(c, name):
    "edit a file related to the server configuration"
    # c.run("SciTE {} &".format(os.path.join(FROM, name)))
    c.run(EDITORCMD.format(os.path.join(FROM, name)))


@task(help={'names': 'comma-separated list of filenames'})
def modconf(c, names=None):
    "deploy modifications for Apache configuration file(s), replace version"
    if names is None:
        return
    names = names.split(',')
    for conf in names:
        shared.mod_conf(c, os.path.join(FROM, conf), A_AVAIL)


@task(help={'names': 'comma-separated list of filenames'})
def modconfb(c, names=None):
    "modconf with backup"
    if names is None:
        return
    names = names.split(',')
    for conf in names:
        shared.mod_conf(c, os.path.join(FROM, conf), A_AVAIL, backup=True)


@task(help={'names': 'comma-separated list of filenames'})
def modconfa(c, names=None):
    "modconf with append (and backup)"
    if names is None:
        return
    names = names.split(',')
    for conf in names:
        shared.mod_conf(c, os.path.join(FROM, conf), A_AVAIL, append=True)


@task(help={'names': 'comma-separated list of filenames'})
def rmconf(c, names=None):
    "disable Apache configuration for one or more file names"
    if names is None:
        return
    names = names.split(',')
    for conf in names:
        shared.remove_conf(c, conf, A_ENABL)


@task
def compare(c):
    "compare all Apache configurations that can be changed from here"
    c.run(f'diff -s {FROM} {A_AVAIL}')


@task
def compareg(c):
    "compare all Apache configurations that can be changed from here, in gui"
    c.run(f'meld {FROM} {A_AVAIL}')
