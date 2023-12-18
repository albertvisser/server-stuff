"""shared routines for INVoke commands
"""
import os
import datetime


def add_conf(c, name, avail, enabl):
    "enable new configuration by creating symlink"
    oldname = os.path.join(avail, name)
    newname = os.path.join(enabl, name)
    c.run(f'sudo ln -s {oldname} {newname}')


def remove_conf(c, name, enabl):
    "disable configuration by removing symlink"
    newname = os.path.join(enabl, name)
    c.run(f'sudo rm {newname}')


def mod_conf(c, name, dest, needs_sudo=True, backup=False, append=False):
    "copy configuration after editing"
    # name = full filename
    if append:
        backup = True
    if backup:
        today = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    frompath, fname = os.path.split(name)

    if backup:
        src = os.path.join(dest, fname)
        trg = os.path.join('backup', f'{fname}-{today}')
        with c.cd(frompath):
            if not os.path.exists(os.path.join(frompath, os.path.dirname(trg))):
                c.run(f'mkdir -m 777 {os.path.dirname(trg)}')
            c.run(f'cp {src} {trg}')

    if append:
        tmp = fname + '~~'
        tmp2 = tmp + '~'
        with c.cd(frompath):
            c.run(f'cp {fname} {tmp}')
            c.run(f'cat {trg} {fname} > {tmp2}')
            c.run(f'mv -f {tmp2} {fname}')

    with c.cd(frompath):
        c.run(f'{{}} cp {fname} {dest}'.format('sudo' if needs_sudo else ''))

    if append:
        with c.cd(frompath):
            c.run(f'mv -f {tmp} {fname}')


def do_compare(local, remote):
    "execute comparison"
    print(f'comparing {local} with {remote}')


def report_result(proj, result):
    """get output of start_server command and save to file(s)
    """
    test = os.umask(0000)
    with open(f'/tmp/server-{proj}-ok', 'w') as _o:
        print(result.stdout, file=_o)
    with open(f'/tmp/server-{proj}-err', 'w') as _o:
        print(result.stderr, file=_o)
    os.umask(test)


def remove_result(c, proj):
    "remove earlier created check files"
    c.run(f'sudo rm -f /tmp/server-{proj}-ok')
    c.run(f'sudo rm -f /tmp/server-{proj}-err')
