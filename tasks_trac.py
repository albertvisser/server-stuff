"""INVoke commands related to Trac server administration
"""
import os.path
from invoke import task
from config import HOME, TRAC, runpath
from tasks_shared import report_result, remove_result

project = os.path.basename(TRAC)
trac_pid = os.path.join(runpath, '{}.pid'.format(project))
trac_sock = os.path.join(runpath, '{}.sock'.format(project))


@task
def stop(c):
    "stop local trac server"
    c.run('sudo kill `cat {}`'.format(trac_pid))
    c.run('sudo rm -f {}'.format(trac_pid))
    remove_result(c, 'trac')


@task
def start(c):  # Note: uses gunicorn for Python 2 (2017-10: still needs to)
    "start local trac server"
    with c.cd(TRAC):
        result = c.run('sudo /usr/bin/gunicorn -D -b unix:{} -p {} '
                       'tracwsgi:application'.format(trac_sock, trac_pid))
        report_result('trac', result)


@task
def restart(c):
    "restart local trac server"
    stop(c)
    start(c)


@task
def editconf(c):
    "alias"
    c.run("fabsrv editconf trac")


@task
def modconf(c):
    "alias"
    c.run("fabsrv modconf -n trac")
