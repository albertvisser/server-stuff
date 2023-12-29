Nginx-config
============

Here are several scripts and files I use in maintaining my local server programs and web applications.
Managing it all is done using a series of Invoke scripts that are started with the command `fabsrv` from my scripts directory - the name remains unchanged from the time I used Fabric for this - and is a shortcut for the invocation `inv --search-root ~/nginx-config $@` ($@ contains all the parameters provided to fabsrv).
This way with `fabsrv --list`  or `fabsrv --help <command>` you can get help info in the standard way invoke defines it.

**tasks.py**
  Besides being the main entry point, this file contains management commands for specific settings
  files not related to server configuration. They are defined in the `misc` section in `config.py`
  and collected in the `misc` subdirectory.

**tasks_nginx.py**
  This file contains functions for managing Nginx as well as the virtual domains I defined for it.
  They are organized bij application/framework type and collected in the `nginx` subdirectory.

**tasks_apache.py**
  This file contains functions for managing Apache as well as the virtual domains I defined for it.
  They are organized bij application/framework type and collected in the `apache` subdirectory.
  Since I don't currently use Apache, they are probably outdated and may not work.

**tasks_php.py**
  This file mainly contains functions for starting and stopping php, which I rarely do.
  I don't much like PHP as a language.

**tasks_ftp.py**
  This file was built specifically for *vsftp*, in my Drupal days, for testing ftp uploads to local
  domains I think. I don't have a local ftp server running I think, so it's probably outdated.

**tasks_django.py**
  This file comtains functions for managing Django wsgi servers as well as some utilities specific
  for working with Django

**tasks_cherrypy.py**
  This file comtains functions for managing CherryPy wsgi servers

**tasks_trac.py**
  This files contains functions for starting and stopping my local trac server, and some shortcuts
  for maintaining the configuration

**tasks_hgweb.py**
  Gitweb works over fastcgi, but Mercurial - being Python - had its own wsgi server. 
  So I needed a separate module to manage it.
 
**tasks_plone.py**
  This file contains functions for starting and stopping and managing the configuration for Plone
  (a CMS built in Python)
  
**tasks_shared.py**
**tasks_sites.py**

Other scripts
.............

``rc.local``
    the standard Linux user startup script, adapted to start my personal servers at bootup
    not used in my current Manjaro setup
``php-fcgi``
    startup script for PHP - not needed anymore?
``hgweb.fcgi``
    startup script for local mercurial server - not used anymore
``apache2nginx.py``
    a script I wrote to partly convert Apache config files to Nginx


Nginx configs:
..............

``default``
    a copy of the config file that came with the installation, with some stuff added - moved into `nginx.config` after changing to Manjaro Linux

At first the others were organized per virtual domain (lemoncurry, pythoneer and magiokis) but I decided organizing per implementation/framework type would be more logical

So I ended up with these configurations:

``cherrypy``
    config for the subdomains powered by CherryPy
``django``
    config for the subdomains that contain Django sites
``drupal``
    configuration for local sites driven by Drupal - obsolete after I stopped using Drupal
``fastcgi``
    config for the sites served using traditional cgi
``flatpages``
    config for local non-dynamic sites (html/css/js only)
``others``
    currently only containing a copy of the previous (flat HTML) version of a Joomla site I maintained but that no longer exists
``plone``
    configuration for local Plone instance(s)
``php-sites``
    config for phppgadmin and the one php site I built
``trac``
    config for my local Trac site, served via Gunicorn - unused because I can't use Trac (no Python 3) 

Apache configs:
...............
Some of the few things I salvaged from my old installation. Roughly the same ones as I use for Nginx, collected in a subdirectory called `apache2` and manageable through routines in the fabfile.


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
``php.ini``
    configuration for php
``hgweb.config``
    configuration for local mercurial web server
``trac.ini``
    configuration for trac server
``gitweb.conf``
    configuration for the git server showing my "central" repositories
``cgitrc``
    configuration for the git server showing my development repositories


Requirements
============

- a Linux/Unix-based system
- Nginx (or Apache for the Apache stuff)
- Python, ~~Fabric~~ Invoke

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
