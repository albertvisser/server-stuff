"""INVoke commands related to Git server administration

no need to start/stop/restart fortunately, so just a command to add a repo to the site
"""
import os.path
from invoke import task
from config import HOME, HGWEB, runpath
from tasks_shared import report_result, remove_result


@task(help={'names': 'comma separated list of repository names (no spaces)',
            'frozen': 'add repo(s) that is moved to the frozen section'})
def addrepo(c, names, frozen=False):
    "add specified repos so that they can be viewed with gitweb"
    for name in names.split(','):
        with c.cd('/var/lib/git'):
            if frozen:
                c.run('sudo ln -s /home/albert/git_repos/.frozen/{0}/.git {0}.git'.format(name))
            else:
                c.run('sudo ln -s /home/albert/git_repos/{0}/.git {0}.git'.format(name))


