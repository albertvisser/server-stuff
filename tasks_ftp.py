"""INVoke commands related to ftp server administration
"""
from invoke import task


@task
def start(c):
    "start vsftpd"
    c.run('sudo start vsftpd')


@task
def stop(c):
    "stop vsftpd"
    c.run('sudo stop vsftpd')


@task
def restart(c):
    "restart vsftpd"
    c.run('sudo restart vsftpd')
