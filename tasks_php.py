"""INVoke commands related to php server administration
"""
from invoke import task


@task
def stop(c):
    "stop php"
    c.run('sudo systemctl stop php-fpm.service')


@task
def start(c):
    "start php"
    c.run('sudo systemctl start php-fpm.service')


@task
def restart(c):
    "restart php"
    c.run('sudo systemctl restart php-fpm.service')
