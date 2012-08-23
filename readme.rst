Nginx-config
------------

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
`others`
    currently empty

non-Nginx configs:
..................

`fcgiwrap.conf`
    config for a general FCGI wrapper
`rst2html.conf`
    CherryPy configuration file
`hosts`
    my local DNS (all kinds of names, all mapped to the local machine)
`rc.local`
    Not strictly a config but a standard Linux startup script, adapted to start my personal servers at bootup
`logviewer.conf`
`rst2html.conf`
    cherrypy server configuration parameters

Scripts:
........

`apache2nginx.py`
    a script I wrote to partly convert Apache config files to Nginx
`fabfile.py`
    script containing the utility functions to manage the above, as in copy the files to the correct locations, (re)start the corresponding servers etc.
`start_logviewer.py`
`start_rst2html.py`
    scripts imported by cherryd to start the application
