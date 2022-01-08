"""INVoke commands related to php server administration
"""
from invoke import task
from config import INIT, PHP

PHPX = 'php7.4-fpm'

@task
def stop(c):
    "stop php"
    # c.run('sudo {}/{} stop'.format(INIT, PHPX))
    c.run('sudo systemctl stop php-fpm7.service')


@task
def start(c):
    "start php"
    # c.run('sudo {}/{} start'.format(INIT, PHPX))
    c.run('sudo systemctl start php-fpm7.service')


@task
def restart(c):
    "restart php"
    # c.run('sudo {}/{} restart'.format(INIT, PHPX))
    c.run('sudo systemctl restart php-fpm7.service')
