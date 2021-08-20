"""INVoke commands related to php server administration
"""
from invoke import task
from config import INIT, PHP

PHPX = 'php7.4-fpm'

@task
def stop(c):
    "stop php"
    c.run('sudo {}/{} stop'.format(INIT, PHPX))


@task
def start(c):
    "start php"
    c.run('sudo {}/{} start'.format(INIT, PHPX))


@task
def restart(c):
    "restart php"
    c.run('sudo {}/{} restart'.format(INIT, PHPX))
