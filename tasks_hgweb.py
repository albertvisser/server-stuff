"""INVoke commands related to Mercurial server administration
"""
import os.path
from invoke import task
from config import HGWEB, runpath
from tasks_shared import report_result, check_result, remove_result

hgweb_pid = os.path.join(runpath, 'hgwebdir.pid')
hgweb_sock = os.path.join(runpath, 'hgwebdir.sock')


@task
def stop(c):
    "stop local Mercurial web server"
    c.run(f'sudo kill `cat {hgweb_pid}`')
    c.run(f'sudo rm -f {hgweb_pid}')
    remove_result(c, 'hgweb')


@task
def start(c):
    "start local Mercurial web server using hgweb.fcgi"
    result = check_result('hgweb')
    if result:
        print('hgweb ' + result)
        return
    # startdir = os.path.join(HGWEB, 'hgweb.fcgi')
    # result = c.run(f'sudo spawn-fcgi -f {startdir} -s {hgweb_sock} -P {hgweb_pid} -u {"www-data"}')
    # gunicorn3 kan mercurial niet importeren; gunicorn2 slaat vast, als ik het niet als daemon
    # uitvoer zie ik
    # Traceback (most recent call last):
    # File "/usr/lib/python2.7/dist-packages/gunicorn/workers/sync.py", line 130, in handle
    #     self.handle_request(listener, req, client, addr)
    # File "/usr/lib/python2.7/dist-packages/gunicorn/workers/sync.py", line 176, in handle_request
    #     for item in respiter:
    # TypeError: 'hgwebdir' object is not iterable
    ## "start local Mercurial web server using gunicorn for Python 3"
    with c.cd(HGWEB):
        result = c.run(f'sudo /usr/bin/gunicorn -D -b unix:{hgweb_sock} -p {hgweb_pid} '
        # result = c.run(f'sudo /usr/bin/gunicorn -b unix:{hgweb_sock} -p {hgweb_pid} '
                       'hgwebwsgi:application')
    report_result('hgweb', result)


@task
def restart(c):
    "restart local Mercurial web server"
    stop(c)
    start(c)
