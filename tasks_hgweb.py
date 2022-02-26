"""INVoke commands related to Mercurial server administration
"""
import os.path
from invoke import task
from config import HOME, HGWEB, runpath
from tasks_shared import report_result, remove_result

hgweb_pid = os.path.join(runpath, 'hgwebdir.pid')
hgweb_sock = os.path.join(runpath, 'hgwebdir.sock')


@task
def stop(c):
    "stop local Mercurial web server"
    c.run('sudo kill `cat {}`'.format(hgweb_pid))
    c.run('sudo rm -f {}'.format(hgweb_pid))
    remove_result(c, 'hgweb')


@task
def start(c):
    "start local Mercurial web server using hgweb.fcgi"
    start = os.path.join(HGWEB, 'hgweb.fcgi')
    result = c.run('sudo spawn-fcgi -f {} -s {} -P {} -u {}'.format(start,
                                                                    hgweb_sock,
                                                                    hgweb_pid,
                                                                    'www-data'))
    report_result('hgweb', result)
    # gunicorn3 kan mercurial niet importeren; gunicorn2 slaat vast, als ik het niet als daemon
    # uitvoer zie ik
    # Traceback (most recent call last):
    # File "/usr/lib/python2.7/dist-packages/gunicorn/workers/sync.py", line 130, in handle
    #     self.handle_request(listener, req, client, addr)
    # File "/usr/lib/python2.7/dist-packages/gunicorn/workers/sync.py", line 176, in handle_request
    #     for item in respiter:
    # TypeError: 'hgwebdir' object is not iterable
    ## "start local Mercurial web server using gunicorn for Python 3"
    ## with c.cd(HGWEB):
        ## c.run('sudo /usr/bin/gunicorn -D -b unix:{} -p {} '
              ## 'hgwebwsgi:application'.format(hgweb_sock, hgweb_pid))


@task
def restart(c):
    "restart local Mercurial web server"
    stop(c)
    start(c)
