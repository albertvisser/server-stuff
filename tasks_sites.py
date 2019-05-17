"""INVoke commands related to my local website stuff
"""
import requests
from invoke import task
from all_local_pages import check_address


def _check_page(address):
    """call up a specific page to inspect the result
    """
    return requests.get('http://' + address)


def _check_frontpage(sitename):
    """simply call the domain to see what response we get back
    """
    r = _check_page(sitename)
    if sitename.startswith('trac'):
        if r.status_code == 401:  # not authenticated is enough for an answer here
            return 200
    return r.status_code


def _get_sitenames():
    """get the names of the local domains from the hosts file
    """
    sites = []
    with open('/etc/hosts') as _in:
        for line in _in:
            if line.startswith('#'):
                continue
            for name in ('lemoncurry', 'magiokis'):
                if name in line:
                    sites.append(line.strip().split()[1])
    return sites


def _check_sites(quick=True, sites=None):
    """alle lokale sites langslopen om te zien of de pagina's werken

    verkorte versie: check alleen de frontpage
    van sommige sites wil je ook zien of vervolgpagina's werken
    vandaar de complete versie:
    van alle lokale sites waar een beperkt aantal vervolgpagina's mogelijk is
    al deze mogelijkheden aflopen
    van gelijksoortige pagina's is één variant voldoende
    """
    sitenames = _get_sitenames()
    if sites:
        sitenames = [name for name in sites if name in sitenames]
    for base in sitenames:
        print('checking {}... '.format(base), end='')
        ok = _check_frontpage(base)
        if ok != 200:
            print('error {}'.format(ok))
            continue
        if quick:
            print('ok')
            if base in check_address['quick']:
                test = base + check_address['quick'][base]
                ok = _check_page(test).status_code
                if ok != 200:
                    print('    error {} on {}'.format(ok, test))
        else:
            print('frontpage ok', end='')
            to_check = []
            if base in check_address['full']:
                if not check_address['full'][base]:
                    print(', no further checking necessary')
                    continue
                print()
                to_read = os.path.join('~', 'nginx-config', 'check-pages', check_address['full'][base])
                to_read = os.path.expanduser(to_read)
                if os.path.exists(to_read):
                    with open(to_read) as _in:
                        to_check = [line.strip() for line in _in]
                    for test in to_check:
                        page = '{}{}'.format(base, test)
                        print('checking {}...'.format(page), end=' ')
                        ok = _check_page(page).status_code
                        if ok == 200:
                            print('ok')
                        else:
                            print('error {}'.format(ok))  # test))
                else:
                    print('    check-pages file missing for {}'.format(base))
            else:
                print()
                print('    check_address entry missing for {}'.format(base))


@task
def check_all(c):
    "quick (frontpage only) check if all local sites are working"
    _check_sites()


@task(help={'names': 'comma-separated list of server names'})
def check_all_pages(c, names):
    "full check if all local sites are working"
    if not args:
        _check_sites(quick=False)
    else:
        _check_sites(quick=False, sites=[x for x in names.split(',')])


