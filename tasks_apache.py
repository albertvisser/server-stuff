"""INVoke commands related to apache server configs
"""
import os.path
from invoke import task
from config import INIT, HERE, A_AVAIL, A_ENABL
import tasks_shared as shared
FROM = os.path.join(HERE, 'apache')


@task
def stop(c):
    "stop apache"
    c.run('sudo {}/apache2 stop'.format(INIT))


@task
def start(c):
    "start apache"
    c.run('sudo {}/apache2 start'.format(INIT))


@task
def restart(c):
    "restart apache"
    c.run('sudo {}/apache2 restart'.format(INIT))


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
    c.run("SciTE {} &".format(os.path.join(FROM, name)))


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
    "compare apache configurations that can be changed from here"
    # TODO: hier zitten ook niet-site-available configs tussen
    for name in os.listdir(FROM):
        shared.do_compare(os.path.join(FROM, name), os.path.join(A_AVAIL, name))
