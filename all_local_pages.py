"""
'lemoncurry'                                    flat
'lemoncurry.nl'                                 flat
'www.lemoncurry.nl'                             flat
'actiereg.lemoncurry.nl'                        django
'albums.lemoncurry.nl'                          django
'myprojects.lemoncurry.nl'                      django
'hg.lemoncurry.nl'                              not-mine
'trac.lemoncurry.nl'                            not-mine
'rst2html.lemoncurry.nl'                        cherrypy
'rst2html_mongo.lemoncurry.nl'                  cherrypy
'mydomains.lemoncurry.nl'       full            django
'myapps.lemoncurry.nl'          full (commented) django
'logviewer.lemoncurry.nl'                       cherrypy
'rstblog.lemoncurry.nl'                         flat
'bitbucket.lemoncurry.nl'                       cherrypy
'bitbucket_mongo.lemoncurry.nl'                 cherrypy
'plone.lemoncurry.nl'                           not-mine
'ragingdragon.lemoncurry.nl'                    not-mine (drupal)
'adr.lemoncurry.nl'                             obsolete?
'films.lemoncurry.nl'                           obsolete?
'muziek.lemoncurry.nl'                          cgi
'absentie.lemoncurry.nl'                        cgi
'doctool.lemoncurry.nl'                         cgi
'original.magiokis.nl'          quick           cgi
'oldlocal.magiokis.nl'                          flat
'local.magiokis.nl'                             not-mine (drupal)
'php.magiokis.nl'               quick           php
'cherrypy.magiokis.nl'          quick           cherrypy
'data.magiokis.nl'                              not accessible
'songs.magiokis.nl'             quick           cgi
'denk.magiokis.nl'              quick           cgi
'dicht.magiokis.nl'             quick           cgi
'vertel.magiokis.nl'            quick           cgi
'django.magiokis.nl'                            django
"""
from __future__ import print_function
import sys
import os
import collections

check_address = {
    'quick': {
        'original.magiokis.nl': '/cgi-bin/mainscript.py',
        'php.magiokis.nl': '/magiokis.php?section=OW&subsection=Home',
        'cherrypy.magiokis.nl': '/ow/',
        'songs.magiokis.nl': '/cgi-bin/lijstsongs.py',
        'denk.magiokis.nl': '/cgi-bin/denk_select.py',
        'dicht.magiokis.nl': '/cgi-bin/dicht_select.py',
        'vertel.magiokis.nl': '/cgi-bin/vertel_select.py',
    },
    'full': {
        'mydomains.lemoncurry.nl': {
            # # /home/albert/projects/mydomains./mydomains/urls.py
            # url(r'^domainchecker/', include('mydomains.index.urls')),
            # url(r'^$', include('mydomains.index.urls')),
            #
            # # Uncomment the admin/doc line below to enable admin documentation:
            # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
            #
            # # Uncomment the next line to enable the admin:
            # url(r'^admin/', include(admin.site.urls)),
            '/domainchecker/',
            '/domainchecker/edit/$',
            '/domainchecker/update/$',
            '/domainchecker/maintain/$',
            '/domainchecker/update_list/$',
        },
        ## 'myapps.lemoncurry.nl': {
    ## url(r'^$', include('myapps.index.urls')),
    ## url(r'^myapps/', include('myapps.index.urls')),
        ## url(r'^$', 'index', name='home'),
        ## url(r'^update/$', 'update'),
        ## url(r'^new/$', 'new'),
        ## url(r'^add/$', 'add'),
    ## url(r'^webapps/', include('myapps.webapps.urls')),
        ## url(r'^$', 'index', name='home'),
        ## url(r'^update/$', 'update'),
        ## url(r'^new/$', 'new'),
        ## url(r'^add/$', 'add'),
        ## }
    },
}


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
        ## print('parsing', location)
        urls = urllist[location]
        location = location.replace('/', '.')
        ## print(urls)
        start = urls.find('patterns(') + 9
        end = urls.rfind(')')
        urlpatterns = urls[start:end].split(',url(')
        ## print(urlpatterns[1:])
        for urlpattern in urls[start:end].split(',url(')[1:]:
            "eerste element is verwijzing naar views module => negeren"
            ## print(urlpattern)
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
        ## for item in result[location]:
            ## print(item)
    return result


def parse_part(urlpart):
    # TODO  uitwerken:
    # (?P<option>(nieuw|add)) betekent twee urls maken
    #   een met de waarde xxx en een met yyy op deze plek
    # (?P<tekst>\d+) betekent dat op deze plek een nummer
    # (?P<option>ok) betekent op deze plek deze vaste waarde
    # (?P<trefw>\w+) betekent op deze plek een woord (spaties(s) niet toegestaan
    # (?P<trefw>(\w|\b)+) betekent op deze plek een frase (spatie(s) wel toegestaan
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
        elif part in (r'(\w|\b)+', r'(\b|\w)+'): # phrase   (?P<trefw>(\w|\b)+)
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
    # domein  voorvoegen
    if project == 'magiokis-django':
        result = ['django.magiokis.nl/{}'.format(x) for x in analyzed]
    else:
        result = ['{}.lemoncurry.nl/{}'.format(project, x) for x in analyzed]
    return result


def discover_django_urls(project):
    """simplistic (!) way of finding urls used in Django project

    assumes al urlconfs are written in a standard fashion
    """
    root = os.path.join('/home/albert/projects', project)
    ## return discover(root)
    ## return parse_result(discover(root))
    return build_urllist(project, parse_result(discover(root)))


if __name__ == '__main__':
    ## print(parse_part('(?P<option>(nieuw|add))'))  # betekent twee urls maken
    ## #   een met de waarde xxx en een met yyy op deze plek
    ## print(parse_part('(?P<tekst>\d+)'))  # betekent dat op deze plek een nummer
    ## print(parse_part('(?P<option>ok)'))  # betekent op deze plek deze vaste waarde
    ## print(parse_part('(?P<trefw>\w+)'))  # betekent op deze plek een woord (spaties(s) niet toegestaan
    ## print(parse_part('(?P<trefw>(\w|\b)+)'))  # betekent op deze plek een frase (spatie(s) wel toegestaan
    ## print(parse_part('(?P<trefw>(\b|\w)+)'))  # betekent op deze plek een frase (spatie(s) wel toegestaan
    ## print(parse_part('(?P<sel>(\w|\s)+)'))  # s staat voor whitespace characters (meer dan spatie)
    ## print(parse_part('hello'))
    ## print(parse_part('\d+'))
    ## print(parse_part('(hello|sailor)'))
    project = sys.argv[1]
    data = discover_django_urls(project)
    with open(project + '-urls.rst', 'w') as _out:
        for x in data:
            print(x, file=_out)
            ## for y in data[x]:
                ## print('   ', y, file=_out)
            ## print('   ', data[x], file=_out)

