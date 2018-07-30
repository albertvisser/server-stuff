# -*- coding: utf-8 -*-
from __future__ import print_function
import pdb
import sys
import os
import collections
import itertools

check_address = {'quick': {
                    'original.magiokis.nl': '/cgi-bin/mainscript.py',
                    'php.magiokis.nl': '/magiokis.php?section=OW&subsection=Home',
                    'cherrypy.magiokis.nl': '/ow/',
                    'songs.magiokis.nl': '/cgi-bin/lijstsongs.py',
                    'denk.magiokis.nl': '/cgi-bin/denk_select.py',
                    'dicht.magiokis.nl': '/cgi-bin/dicht_select.py',
                    'vertel.magiokis.nl': '/cgi-bin/vertel_select.py', },
                 'full': {
                    # platte html hoeft wat mij betreft niet meer dan index pagina
                    'lemoncurry': None,
                    'lemoncurry.nl': None,
                    'www.lemoncurry.nl': None,
                    'rstblog.lemoncurry.nl': None,
                    'bitbucket.lemoncurry.nl': None,
                    'bitbucket_mongo.lemoncurry.nl': None,
                    'oldlocal.magiokis.nl': None,
                    'data.magiokis.nl': None,
                    # Drupal en andere frameworks hoeft van mij ook niet
                    'ragingdragon.lemoncurry.nl': None,
                    'local.magiokis.nl': None,
                    'plone.lemoncurry.nl': None,
                    'hg.lemoncurry.nl': None,
                    'trac.lemoncurry.nl': None,
                    # platte CGI wel
                    'muziek.lemoncurry.nl': 'albums-cgi-urls.rst',
                    'absentie.lemoncurry.nl': 'absentie-urls.rst',
                    'doctool.lemoncurry.nl': 'doctool-urls.rst',
                    'original.magiokis.nl': 'original-urls.rst',
                    'songs.magiokis.nl': 'songs-urls.rst',
                    'denk.magiokis.nl': 'denk-urls.rst',
                    'dicht.magiokis.nl': 'dicht-urls.rst',
                    'vertel.magiokis.nl': 'vertel-urls.rst',
                    # php-cgi ook
                    'php.magiokis.nl': 'magiokis-php-urls.rst',
                    # Django wel
                    'mydomains.lemoncurry.nl': 'mydomains-urls.rst',
                    'myapps.lemoncurry.nl': 'myapps-urls.rst',
                    'myprojects.lemoncurry.nl': 'myprojects-urls.rst',
                    'actiereg.lemoncurry.nl': 'actiereg-urls.rst',
                    'albums.lemoncurry.nl': 'albums-urls.rst',
                    'django.magiokis.nl': 'magiokis-django-urls.rst',
                    # Cherrypy ook
                    'cherrypy.magiokis.nl': 'magiokis-cherry-urls.rst',
                    'rst2html.lemoncurry.nl': 'rst2html-urls.rst',
                    'rst2html_mongo.lemoncurry.nl': 'rst2html-urls.rst',
                    'logviewer.lemoncurry.nl': 'logviewer-urls.rst', }, }


def discover(here, root=None, urllist=None):
    "inspect urls.py and/or search further"
    if root is None:
        root = here
    if urllist is None:
        urllist = {}
    for name in os.listdir(here):
        test = os.path.join(here, name)
        if os.path.isfile(test) and name == 'urls.py':
            data = []
            got_patterns = False
            with open(test) as _in:
                for line in _in:
                    inline = line.strip().split('#')[0]
                    if 'patterns(' in inline:
                        got_patterns = True
                    if got_patterns:
                        data.append(inline)
            urllist[test.split(root)[1][1:-3]] = ''.join(data).replace("''","")
        elif os.path.isdir(test):
            urllist.update(discover(test, root, urllist))
    return urllist


def sortlocs(x):
    return len(x.split('/')), x


def parse_result(urllist):
    result = collections.defaultdict(list)
    prefixes = {}
    for location in sorted(urllist, key=sortlocs):
        urls = urllist[location]
        location = location.replace('/', '.')
        start = urls.find('patterns(') + 9
        end = urls.rfind(')')
        urlpatterns = urls[start:end].split(',url(')
        for urlpattern in urls[start:end].split(',url(')[1:]:
            "eerste element is verwijzing naar views module => negeren"
            urlstuff = urlpattern.split(',')
            pattern = urlstuff[0].split("r'^", 1)[1]
            if pattern.startswith('admin'):
                continue
            test = urlstuff[1].strip()
            if test.startswith('include'):
                prefixes[test.split("'")[1]] = pattern.rstrip("'")
            else:
                url = prefixes.get(location, '') + pattern
                result[location].append(url.rstrip("$'"))
    return result


def parse_part(urlpart):
    # TODO  uitwerken:
    # (?P<option>(nieuw|add)) betekent twee urls maken
    #   een met de waarde xxx en een met yyy op deze plek
    # (?P<tekst>\d+) betekent dat op deze plek een nummer
    # (?P<option>ok) betekent op deze plek deze vaste waarde
    # (?P<trefw>\w+) betekent op deze plek een woord (spaties(s) niet toegestaan
    # (?P<trefw>(\w|\b)+) betekent op deze plek een frase (spatie(s) wel toegestaan
    # (?P<msg>.+) betekent ...
    # (?P<sel>(\w|\s)+) s staat voor whitespace characters (meer dan spatie)
    # dit zijn denk ik de belangrijkste
    if urlpart.startswith('('):
        part = urlpart[1:-1] # remove parentheses
        if part.startswith('?P<'):
            part = part.split('>', 1)[1] # we don't care about the group name here
        else:
            return ['unexpected url part: <{}>'.format(urlpart)]
        # special cases:
        if part == '\d+': # digits
            part = '<number>'
        elif part == '\w+': # characters
            part = '<word>'
        elif part in (r'(\w|\b)+', r'(\b|\w)+', '.+'): # phrase   (?P<trefw>(\w|\b)+)
            part = '<phrase>'
        elif part == '(\w|\s)+': # phrase                   (?P<sel>(\w|\s)+)
            part = '<message>'
        elif '|' in part: # alternatives
            part = part[1:-1] # remove parentheses
            return part.split('|')
        else:
            part = part
        return [part]
    elif urlpart.startswith('\\'):
        return ['unexpected url part: <{}>'.format(urlpart)] # TODO do I need to handle this?
    else:
        return [urlpart]


def build_urllist(project, result):
    """platslaan, sorteren en domein voorvoegen
    tevens regexp analyseren en echte urls bouwen
    """
    ## data = sorted([x for x in (y for y in result.values())])
    unsorted = []
    # platslaan
    for x in result.values():
        unsorted.extend([y for y in x])
    # sorteren en regexp analyseren
    analyzed = []
    for x in sorted(unsorted):
        parts = x.split('/')                #per urldeel een string
        ready = []                          # list of lists
        for part in parts:                  # voor elk urldeel:
            newparts = parse_part(part)     # zet urldeel om naar 1 of meer strings
            if not ready:
                ready = newparts
            else:
                newready = []
                for newpart in newparts:
                    for item in ready:
                        newready.append('/'.join((item, newpart)))
                ready = newready
        analyzed.extend(ready)
    result = analyzed
    # domein  voorvoegen - alleen / is voldoende
    ## if project == 'magiokis-django':
        ## result = ['django.magiokis.nl/{}'.format(x) for x in analyzed]
    ## else:
        ## result = ['{}.lemoncurry.nl/{}'.format(project, x) for x in analyzed]
    result = ['/{}'.format(x) for x in analyzed]
    return result


def discover_django_urls(project):
    """simplistic (!) way of finding urls used in Django project

    assumes al urlconfs are written in a standard fashion
    """
    root = os.path.join('/home/albert/projects', project)
    ## return discover(root)
    ## return parse_result(discover(root))
    return build_urllist(project, parse_result(discover(root)))


def do_logviewer():
    """
    introspectie is waarschijnlijk netter, maar eerst maar even plat lezen:
    """
    data = []
    with open('/home/albert/projects/logviewer/viewlogs_cherry.py') as _in:
        data = _in.readlines()
    exposed = False
    views = []
    for line in data:
        if exposed:
            views.append(line.strip())
            exposed = False
        elif '@cherrypy.expose' in line:
            exposed = True
    urls = []
    for line in [x.replace('def ', '').replace('self', '') for x in views]:
        if 'index' in line:
            url = '/'
        elif '()' in line:
            urls.append('/' + line.replace('():', '/'))
            continue
        else:
            url = '/' + line[:line.index('(')].strip() + '/'
        needed, optional = [], []
        for param in line[line.index('(') + 1:line.index(')')].split(','):
            param = param.strip()
            if '=' in param:
                optional.append(param[:param.index('=')])
            elif param:
                needed.append(param)
        url2 = ''
        if needed:
            url += '?' + '=<>&'.join(needed) + '=<>'
            url2 = url + '=<>&'.join(optional) + '=<>'
        elif optional:
            url2 = url + '?' + '=<>&'.join(optional) + '=<>'
        urls.append(url)
        if url2:
            urls.append(url2)
    return urls


def do_rst2html():
    """
    de views kunnen allemaal dezelfde set argumenten verwerken; aan de functie
    die wordt aangeroepen kun je zien welke argumenten werkelijk vereist zijn
    """
    data = []
    with open('/home/albert/projects/rst2html/rst2html.py') as _in:
        data = _in.readlines()
    exposed = False
    urls = []
    for line in data:
        line = line.strip()
        if line.startswith('#'):
            continue
        if exposed:
            if 'def' in line:
                view = line  # we only need the function name, so one line is enough
                url = '/' + view[:view.index('(')].replace('def ', '') + '/'
                if url == '/index/':
                    url = '/'
                body = []
                in_docstring = False
            elif 'return' in line:
                exposed = False
                # look at called function(s) - calls are immediately relayed so we can use
                # their arguments
                body = ''.join(body)
                params = body[body.index('(') + 1:body.index(')')]
                if params:
                    args = [x.strip() for x in params.split(',')]
                    url += '?' + '=<>&'.join(args) + '=<>'
                urls.append(url)
            else:
                if not in_docstring and line.startswith('"""'):
                    in_docstring = True
                    line = line[3:]
                if in_docstring:
                    if line.endswith('"""'):
                        in_docstring = False
                    continue
                try:
                    line = line[line.index('#'):]
                except ValueError:
                    pass
                body.append(line)
        elif '@cherrypy.expose' in line:
            exposed = True
            ## pdb.set_trace()
    return urls


def do_magiokis():
    """
    er worden attributen aangemaakt voor de secties bv. self.ow = OldWhoresPage()
    dwz dat is het eerste onderdeel van de url bv /ow/
    bij SpeelMee wordt dat trucje herhaald
    de naam van een functie is bepalend voor het vervolgdeel van de url
    met dien verstande dat index de / locatie is en default ook wordt ingeslikt
    (maar dan is er sprake van extra parameters)
    """
    def getnamestuff(name):
        name == test[1].rstrip(':')
        needed, optional = [], []
        if '(' in name:
            ix1 = name.index('(')
            ix2 = name.index(')')
            params = name[ix1 + 1:ix2].split(',')
            name = name[:ix1]
            for parm in params:
                parm = parm.strip()
                if parm == 'self':
                    continue
                if '=' in parm:
                    name2, val = [x.strip() for x in parm.split('=')]
                    name2 = '<{}>'.format(name2)
                    if val != "''":
                        name2 += val.strip("'")
                    optional.append(name2)
                else:
                    needed.append('<{}>'.format(parm))
        return name, needed, optional


    urls = []
    data = []
    with open('/home/albert/projects/magiokis-cherry/magiokis.py') as _in:
        data = _in.readlines()
    # lees class
    # als __init__ methode dan (sub)secties
    # index is /
    # default verdient verder analyseren
    # andere naam is pagina adres
    exposed = in_init = in_docstring = False
    sections = collections.defaultdict(dict)
    urls = collections.defaultdict(list)
    classname = ''
    for line in data:
        line = line.strip()
        if not line:
            if in_init:
                for line in body:
                    if line.startswith('self.'):
                        test = line.replace('self.', '').split(' = ')
                        sections[classname][test[1].replace('()', '')] = test[0]
                in_init = False
            continue
        if line.startswith('#'):
            continue
        if line == '@cherrypy.expose':
            exposed = True
            continue
        test = line.strip().split(None, 1)
        if test[0] == 'class':
            classname = getnamestuff(test[1])[0]
            ## if classname == 'HomePage':
                ## urlbase = '/'
        elif not classname:
            continue
        elif test[0] == 'def':
            viewname, args, opts = getnamestuff(test[1])  # assumes function call only spans one line
            if viewname == '__init__':
                in_init = True
                body = []
            elif exposed:
                if args or opts:
                    print('found def:', classname, viewname)
                    print('args:', args)
                    print('opts:', opts)
                if viewname == 'index':
                    urls[classname].append('/')
                    urlbasename = ''
                elif viewname == 'default':
                    urlbasename = ' '
                else:
                    urlbasename = '/' + viewname
                if urlbasename:
                    if args:
                        urlbasename += '/' + '/'.join(args)
                    urllist = [urlbasename.strip()]
                    for item in opts:
                        if item.endswith('>'):
                            ## print(urllist, item)
                            urllist = ['/'.join((x, item)) for x in urllist]
                        else:
                            dflt = item[item.index('>') + 1:]
                            urllist1 = ['/'.join((x, dflt)) for x in urllist]
                            item = item.replace(dflt, '')
                            urllist2 = ['/'.join((x, item)) for x in urllist]
                            urllist = urllist1 + urllist2
                    ## if opts:
                        urls[classname].extend(urllist)
                    urls[classname].append(urlbasename.strip())
                in_docstring = False
        elif test[0] == 'return':
            ## if in_init:
                ## for line in body:
                    ## if line.startswith('self.'):
                        ## test = line.replace('self.', '').split(' = ')
                        ## sections[classname][test[1].replace('()', '')] = test[0]
            ## in_init = False
            exposed = False
        elif in_init:
            if not in_docstring and line.startswith('"""'):
                in_docstring = True
                line = line[3:]
            if in_docstring:
                if line.endswith('"""'):
                    in_docstring = False
                continue
            try:
                line = line[line.index('#'):]
            except ValueError:
                pass
            body.append(line)
    homepagekey = 'HomePage:'
    for key in sections:
        if key == homepagekey:
            continue
        for item, value in sections[key].items():
            prefix = sections[homepagekey][key]
            sections[homepagekey][item] = '/'.join((prefix, value))
    final = []
    for section, urllist in urls.items():
        if section == homepagekey:
            continue
        newlist = [sections[homepagekey][section].join(('/', x)) for x in urllist]
        for ix, item in enumerate(newlist):
            if not item.endswith('/'):
                newlist[ix] += '/'
        final.extend(newlist)
    final.extend(urls[homepagekey])
    return sorted(final)


def discover_cherrypy_urls(project):
    """om te beginnen even een opsomming van wat ik aantref in de diverse scripts
    en hoe daarmee om te gaan:
    - bepaal class
    - selecteer methoden gedecoreerd met @cherrypy.expose
    - hoe link je een view aan een url?
    - anders dan bij django werken deze allemaal verschillend
    """
    if project == 'logviewer':
        result = do_logviewer()
    elif project == 'magiokis-cherry':
        result = do_magiokis()
    elif project == 'rst2html':
        result = do_rst2html()
    return result


def do_magiokis_php():
    """
    """
    # zoek naar $_GET (of $_POST etc) in php files?
    # en dan kijken door welke deze geïmporteerd worden?


def do_plaincgi(project, getdetails=False):
    """Analyse the site's scripts directory to collect the various parameters that can be
    provided
    only examine files that are marked executable
    """
    root = os.path.join(os.path.expanduser('~'), 'projects', project, 'cgi-bin')
    parms = collections.defaultdict(list)
    for name in os.listdir(root):
        # file moet executable zijn
        path = os.path.join(root, name)
        if not os.path.isfile(path):
            continue
        test = os.stat(path).st_mode
        import stat
        if not test & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            continue
        if not getdetails:  # we only want the pages / script names
            parms[name] = []
            continue
        # en nu dan proberen de mogelijke aanroepen te bepalen
        with open(path) as _in:
            lines = _in.readlines()
        searchfor = []
        for line in lines:
            # 1. bepaal aan welke variabele de FieldStorage wordt gekoppeld
            if 'FieldStorage' in line and '=' in line:
                pos = line.index('FieldStorage')
                parts = line[:pos].rsplit('=', 1)
                fs_item = parts[0].rstrip().rsplit(' ', 1)[1]
                searchfor = ['{}.getfirst'.format(fs_item),
                             '{}.getlist'.format(fs_item),
                             ' in {}'.format(fs_item)]
                continue
            # 2. bepaal welke variabelen er uit gehaald worden, meestal zal dat met "getfirst"
            # zijn of getlist maar ik weet niet of ik dat vaak gebruik
            # het kan ook zijn dat dat er alleen op aanwezigheid wordt getest met "in"
            while line:
                found = False
                for ix, item in enumerate(searchfor):
                    if item in line:
                        found = True
                        pos = line.index(item)
                        if ix == 2:
                            arg_name = line[:pos].rstrip().rsplit(' ', 1)[1]
                            pos += len(item)
                        else:
                            startpos = line[pos:].index('(')
                            endpos = line[pos:].index(')')
                            arg_name = line[pos:][startpos + 1:endpos]
                            if ',' in arg_name:
                                arg_name = arg_name[:arg_name.index(',')]
                            pos += endpos
                        parms[name].append(arg_name)
                        line = line[pos:]
                        break
                if not found:
                    break
    # helaas heb ik dan nog geen idee van het type / mogelijke waarden hiervan
    # laat staan in welke combinaties ze kunnen voorkomen
    return parms


def build_combos(using_list):
    combos = []
    for arg in using_list:
        combos.append((arg,))
    for length in range(2, len(using_list)):
        newcombos = [x for x in itertools.combinations(using_list, length)]
        combos.extend(newcombos)
    combos.append(using_list)
    return combos


def add_site(project, pagename):
    if project in ('absentie', 'doctool'):
        return "http://{}.lemoncurry.nl/{}".format(project, pagename)
    if project == 'albums-cgi':
        return "http://muziek.lemoncurry.nl/{}".format(project, pagename)
    # project == 'magiokis'
    for name in ('denk', 'dicht', 'vertel'):
        if pagename.startswith(name):
            return "http://{}.lemoncurry.nl/{}".format(name, pagename)
    for name in ('lijst', 'songs', 'wijzig'):
        if pagename.startswith(name):
            return "http://songs.lemoncurry.nl/{}".format(pagename)
    return "http://original.lemoncurry.nl/{}".format(pagename)


def build_fcgi_urls(project, parmdict):
    results = []
    for page, args in parmdict.items():
        using = set()
        for item in args:
            for char in ('"', "'"):
                if item.startswith(char):
                    using.add(item.strip(char))
        combos = build_combos(list(using))
        for parmlist in combos:
            address = '/cgi-bin/{}?'.format(page)
            results.append(address + '&'.join(['{}=<value>'.format(x) for x in parmlist]))
    return results


def discover_fcgi_urls(project, getdetails=False):
    if project == 'magiokis-php':
        result = do_magiokis_php()
    else:
        # for now getdetails will always be False
        argdict = do_plaincgi(project, getdetails)
        if getdetails:
            result = build_fcgi_urls(project, argdict)
        else:
            result = ['/cgi-bin/' + x for x in argdict.keys()]
    return result


def test_parse_part():
    for item in [r'(?P<option>(nieuw|add))',  # betekent twee urls maken: één met de waarde xxx
                                              # en één met yyy op deze plek
                 r'(?P<tekst>\d+)',           # betekent op deze plek een nummer
                 r'(?P<option>ok)',           # betekent op deze plek deze vaste waarde
                 r'(?P<trefw>\w+)',          # op deze plek een woord (spaties(s) niet toegestaan
                 r'(?P<trefw>(\w|\b)+)',      # op deze plek een frase (spatie(s) wel toegestaan
                 r'(?P<trefw>(\b|\w)+)',      # op deze plek een frase (spatie(s) wel toegestaan
                 r'(?P<sel>(\w|\s)+)',        # s staat voor whitespace (meer dan spatie)
                 'hello',
                 r'\d+',
                 '(hello|sailor)']:
        print(parse_part(item))


if __name__ == '__main__':
    sys.path.append('/home/albert/bin')
    import settings as repos
    project = sys.argv[1]
    if project in repos.cherrypy_repos:
        data = discover_cherrypy_urls(project)
    elif project in repos.django_repos or project == "mydomains":
        data = discover_django_urls(project)
    elif project in repos.fcgi_repos:
        data = discover_fcgi_urls(project)
    else:
        data = []
    if data:
        if project == 'magiokis':
            with open('denk-urls.rst', 'w') as _denk, \
                 open('dicht-urls.rst', 'w') as _dicht, \
                 open('vertel-urls.rst', 'w') as _vertel, \
                 open('songs-urls.rst', 'w') as _songs, \
                 open('original-urls.rst', 'w') as _out:
                for x in data:
                    if x.startswith('/cgi-bin/denk'):
                        print(x, file=_denk)
                    elif x.startswith('/cgi-bin/dicht'):
                        print(x, file=_dicht)
                    elif x.startswith('/cgi-bin/vertel'):
                        print(x, file=_vertel)
                    elif x.startswith('/cgi-bin/songs') \
                            or x.startswith('/cgi-bin/lijst') \
                            or x.startswith('/cgi-bin/wijzig'):
                        print(x, file=_songs)
                    else:
                        print(x, file=_out)
        else:
            with open(project + '-urls.rst', 'w') as _out:
                for x in data:
                    print(x, file=_out)
    else:
        print("not possible with this tool")

