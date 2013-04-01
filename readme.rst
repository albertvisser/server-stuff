Nginx-config
============

When I transferred my system from Ubuntu to Linux Mint I also decided to trade in Apache for Nginx. It took me quite some time to get to grips with it and I found myself building and copying and rearranging config files all of the time. I'd read some about Fabric, a Python package to facilitate that kind of stuff, read it again and decided to give it a try - very satisfactory indeed.

Besides the actual Nginx configuration files (or rather: includes) I collected some other configurations here so they are centralized and version controlled as well. And of course the script to manage it all is here.

Files:
......

`default`
    a copy of the config file that came with the installation
`lemoncurry`
    configuration for flat HTML, CGI and php subdomains on my home server
`magiokis`
    another one, for another series of those domains
`pythoneer`
    and another one
`mercurial`
    config for serving my local Mercurial repositories
`trac`
    config for my local Trac site
`django`
    config for the subdomains that contain Django sites
`cherrypy`
    config for the subdomains powered by CherryPy
`drupal`
    configuration for local sites driven by Drupal
`joomla`
    configuration for local Joomla sites
`plone`
    configuration for local Plone instance
`others`
    currently containing a copy of the previous version of a site I maintain

non-Nginx configs:
..................
configs that are not in user-editable directories (e.g. in /etc) or only here

`fcgiwrap.conf`
    config for a general FCGI wrapper
`logviewer.conf`, `rst2html.conf`
    cherrypy server configuration parameters
`hosts`
    my local DNS (all kinds of names, all mapped to the local machine)
`rc.local`
    Not strictly a config but a standard Linux startup script, adapted to start my personal servers at bootup
`nginx.conf`
    base configuration for nginx
`apache2.conf`
    base configuration for Apache
`php-fcgi`
    startup script for PHP
`ports.conf`
    port configuration for Apache serving on port 81

Apache configs:
...............
Some of the few things I salvaged from my old installation.
Roughly the same ones as I use for Nginx, collected in a subdirectory called `apache2`
and managable through routines in the fabfile.

Scripts:
........

`apache2nginx.py`
    a script I wrote to partly convert Apache config files to Nginx
`fabfile.py`
    script containing the utility functions to manage the above, as in
    copy the files to the correct locations,
    (re)start the corresponding servers
    etc.
`start_logviewer.py`, `start_rst2html.py`, `start_magiokis.py`
    scripts imported by cherryd to start specific applications

Requirements
============

- a Linux/Unix-based system
- Nginx (or Apache for the Apache stuff)
- Python

where applicable:

- php
- Django
- CherryPy
- Mercurial
- Trac
- Joomla
- Drupal
- Plone
