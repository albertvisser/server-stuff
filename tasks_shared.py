"""shared routines for INVoke commands
"""
import os
import datetime


def add_conf(c, name, avail, enabl):
    "enable new configuration by creating symlink"
    oldname = os.path.join(avail, name)
    newname = os.path.join(enabl, name)
    c.run('sudo ln -s {} {}'.format(oldname, newname))


def remove_conf(c, name, enabl):
    "disable configuration by removing symlink"
    newname = os.path.join(enabl, name)
    c.run(' sudo rm {}'.format(newname))


def mod_conf(c, name, dest, needs_sudo=True, backup=False, append=False):
    "copy configuration after editing"
    # name = full filename
    if append: backup = True
    if backup:
        today = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    frompath, fname = os.path.split(name)

    if backup:
        src = os.path.join(dest, fname)
        trg = os.path.join('backup', '-'.join((fname, today)))
        with c.cd(frompath):
            if not os.path.exists(os.path.join(frompath, os.path.dirname(trg))):
                c.run('mkdir -m 777 {}'.format((os.path.dirname(trg))))
            c.run('cp {} {}'.format(src, trg))

    if append:
        tmp = fname + '~~'
        tmp2 = tmp + '~'
        with c.cd(frompath):
            c.run('cp {} {}'.format(fname, tmp))
            c.run('cat {} {} > {}'.format(trg, fname, tmp2))
            c.run('mv -f {} {}'.format(tmp2, fname))

    with c.cd(frompath):
        c.run('{} cp {} {}'.format('sudo' if needs_sudo else '', fname, dest))

    if append:
        with c.cd(frompath):
            c.run('mv -f {} {}'.format(tmp, fname))


def do_compare(local, remote):
    "execute comparison"
    print('comparing {} with {}'.format(local, remote))


def report_result(proj, result):
    """get output of start_server command and save to file(s)
    """
    test = os.umask(0000)
    with open('/tmp/server-{}-ok'.format(proj), 'w') as _o:
        print(result.stdout, file=_o)
    with open('/tmp/server-{}-err'.format(proj), 'w') as _o:
        print(result.stderr, file=_o)
    os.umask(test)


def remove_result(c, proj):
    "remove earlier created check files"
    c.run('sudo rm -f /tmp/server-{}-ok'.format(proj))
    c.run('sudo rm -f /tmp/server-{}-err'.format(proj))
