"""INVoke commands related to Trac server administration
"""
import os.path
from invoke import task
from config import TRAC, runpath
from tasks_shared import report_result, check_result, remove_result

project = os.path.basename(TRAC)
trac_pid = os.path.join(runpath, f'{project}.pid')
trac_sock = os.path.join(runpath, f'{project}.sock')


@task
def stop(c):
    "stop local trac server"
    c.run(f'sudo kill `cat {trac_pid}`')
    c.run(f'sudo rm -f {trac_pid}')
    remove_result(c, 'trac')


@task
def start(c):
    "start local trac server"
    result = check_result('trac')
    if result:
        print('trac ' + result)
        return
    with c.cd(TRAC):
        # result = c.run(f'sudo /usr/bin/gunicorn -D -b unix:{trac_sock} -p {trac_pid} '
        #                'tracwsgi:application')
        # result = c.run(f'sudo tracd -d --pidfile={trac_pid} -p 9000'
        #                f' --basic-auth="*,{TRAC}/trac_users, lemontrac" --protocol=http -s {TRAC}')
        result = c.run(f'sudo /home/albert/.tracvenv/bin/tracd -d --pidfile={trac_pid} -p 9000'
                       f' --basic-auth="*,{TRAC}/trac_users, lemontrac" --protocol=http -s {TRAC}')
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
