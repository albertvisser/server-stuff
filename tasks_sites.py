"""INVoke commands related to my local website stuff
"""
import os.path
import requests
from invoke import task
from all_local_pages import check_address
HOSTS = '/etc/hosts'


@task
def list_domains(c):
    "list all domains that can be checked with these routines"
    print('defined domains:')
    for name in get_sitenames():
        print(name)


@task
def check_up(c):
    "quick (frontpage only) check if all local sites are working"
    check_sites(up_only=True)


@task
def check_all(c):
    "check if selected pages on all local sites are working"
    check_sites()


@task(help={'names': 'comma-separated list of server names'})
def check_pages(c, names):
    "full check if the named local sites are working"
    check_sites(quick=False, sites=[x for x in names.split(',')])


@task
def check_all_pages(c):
    "full check if all local sites are working"
    check_sites(quick=False)


@task(help={'names': 'comma-separated list of server names'})
def check_project(c, names):
    "check if pages for specific projects are up"
    sites = []
    for name in names.split(','):
        if name == 'magiokis':
            sites += [x + '.magiokis.nl' for x in ('original', 'songs', 'vertel', 'denk', 'dicht')]
        elif name.startswith('magiokis'):
            sites += [name.split('-')[1] + '.magiokis.nl']
        elif name == 'rst2html':
            sites += ['{}{}.lemoncurry.nl'.format(name, x) for x in ('', '-mongo', '-pg')]
        else:
            sites += [name + '.lemoncurry.nl']
    check_sites(quick=False, sites=sites)


def check_sites(up_only=False, quick=True, sites=None):
    """alle lokale sites langslopen om te zien of de pagina's werken

    verkorte versie: check alleen de frontpage
    van sommige sites wil je ook zien of vervolgpagina's werken
    vandaar de complete versie:
    van alle lokale sites waar een beperkt aantal vervolgpagina's mogelijk is
    al deze mogelijkheden aflopen
    van gelijksoortige pagina's is één variant voldoende
    """
    sitenames = get_sitenames()
    if sites:
        sitenames = [name for name in sites if name in sitenames]
    for base in sitenames:
        print('checking {}... '.format(base), end='')
        ok = check_frontpage(base)
        if ok != 200:
            print('error {}'.format(ok))
            continue
        if up_only:
            print('ok')
            continue
        if quick:
            print('ok')
            if base in check_address['quick']:
                test = base + check_address['quick'][base]
                ok = check_page(test).status_code
                if ok != 200:
                    print('    error {} on {}'.format(ok, test))
            continue
        print('frontpage ok', end='')
        to_check = []
        if base in check_address['full']:
            if not check_address['full'][base]:
                print(', no further checking necessary')
                continue
            print()
            to_read = os.path.join('~', 'nginx-config', 'check-pages',
                                   check_address['full'][base])
            to_read = os.path.expanduser(to_read)
            if os.path.exists(to_read):
                with open(to_read) as _in:
                    to_check = [line.strip() for line in _in]
                for test in to_check:
                    page = '{}{}'.format(base, test)
                    print('    checking {}...'.format(page), end=' ')
                    ok = check_page(page).status_code
                    if ok == 200:
                        print('ok')
                    else:
                        print('error {}'.format(ok))  # test))
            else:
                print('    check-pages file missing for {}'.format(base))
        else:
            print()
            print('    check_address entry missing for {}'.format(base))


def check_page(address):
    """call up a specific page to inspect the result
    """
    return requests.get('http://' + address)


def check_frontpage(sitename):
    """simply call the domain to see what response we get back
    """
    r = check_page(sitename)
    if sitename.startswith('trac'):
        if r.status_code == 401:  # not authenticated is enough for an answer here
            return 200
    return r.status_code


def get_sitenames():
    """get the names of the local domains from the hosts file
    """
    sites = []
    with open(HOSTS) as _in:
        for line in _in:
            if line.startswith('#'):
                continue
            for name in ('lemoncurry', 'magiokis'):
                if name in line:
                    sites.append(line.strip().split()[1])
    return sites
