Nginx-config
============

When I transferred my system from Ubuntu to Linux Mint I also decided to trade in Lighttpd for Nginx. It took me quite some time to get to grips with it and I found myself building and copying and rearranging config files all of the time. I'd read some about Fabric, a Python package to facilitate that kind of stuff, read it again and decided to give it a try - and it turned out very satisfactory indeed.

Besides the actual Nginx configuration files (or rather: includes) I collected some other configurations here so they are centralized and version controlled as well. And of course the script to manage it all is here.

Nginx configs:
..............

``default``
    a copy of the config file that came with the installation
``lemoncurry``
    configuration for various subdomains on my home server
``magiokis``
    another one, for another series of those domains
``pythoneer``
    and another one
``mercurial``
    config for serving my local Mercurial repositories
``trac``
    config for my local Trac site, served via Gunicorn
``trac_via_tracd``
    older config running tracd over port 9001 instead of over a socket
``django``
    config for the subdomains that contain Django sites
``cherrypy``
    config for the subdomains powered by CherryPy
``drupal``
    configuration for local sites driven by Drupal
``joomla``
    configuration for local Joomla sites
``plone``
    configuration for local Plone instance
``others``
    currently only containing a copy of the previous (flat HTML) version of a Joomla site I maintain

Apache configs:
...............
Some of the few things I salvaged from my old installation. Roughly the same ones as I use for Nginx, collected in a subdirectory called `apache2` and managable through routines in the fabfile.


Other configs:
..................
configs that are not in user-editable directories (e.g. in /etc) or only here

``fcgiwrap.conf``
    config for a general FCGI wrapper
``hosts``
    my local DNS (all kinds of names, all mapped to the local machine)
``nginx.conf``
    base configuration for nginx
``apache2.conf``
    base configuration for Apache
``ports.conf``
    port configuration for Apache serving on port 81
``hgweb.config``
    configuration for local mercurial web server
``trac.ini``
    configuration for trac server
``buildout.cfg`` (plone-conf)
    configuration for plone (not under vc)

Scripts:
........

``rc.local``
    the standard Linux user startup script, adapted to start my personal servers at bootup
``php-fcgi``
    startup script for PHP
``hgweb.cgi`` ``hgweb.fcgi`` ``hgweb.wsgi``
    startup script for local mercurial server
``trac.fcgi``
    alternate startup script for running trac over gunicorn (not under vc)
``fabfile.py``
    script containing the utility functions to manage the above, as in
    copy the files to the correct locations,
    (re)start the corresponding servers
    etc.
``apache2nginx.py``
    a script I wrote to partly convert Apache config files to Nginx

Requirements
============

- a Linux/Unix-based system
- Nginx (or Apache for the Apache stuff)
- Python, Fabric

where applicable:

- PHP
- Django
- CherryPy
- Mercurial
- Trac
- Joomla
- Drupal
- Plone
- Gunicorn
