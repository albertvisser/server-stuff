import sys
import os
INLOC = '/home/albert/van_backup/etc/apache2/sites-available'
OUTLOC = '/home/albert/nginx-config'
USAGE = """\
usage: [python] apache2nginx.py <basename>

takes a file in {}
and converts it to a same-named file in {}
""".format(INLOC, OUTLOC)

def zetom(infile, outfile):
    "zet per virtual host de apache statements een voor een om in nginx statements"
    with open(infile) as _in, open(outfile, "w") as _out:
        for line in _in:
            words = line.strip().split()
            if len(words) == 0:
                _out.write('\n')
            elif line == '<VirtualHost *:80>\n':
                _out.write('server {\n')
            elif words[0] == 'ServerName':
                _out.write('    server_name {};\n'.format(words[1]))
            elif words[0] == 'DocumentRoot':
                _out.write('    root {};\n'.format(words[1].strip('"')))
            elif words[0] == 'ScriptAlias':
                _out.write('    #script_alias {};\n'.format(words[2].strip('"')))
            elif words[0] == 'ErrorLog':
                _out.write('    error_log {} warn;\n'.format(
                    words[1].replace('/var/log/apache2', 'logs')))
            elif words[0] == 'CustomLog':
                _out.write('    access_log {} main;\n'.format(
                    words[1].replace('/var/log/apache2', 'logs')))
            elif line == '</VirtualHost>\n':
                _out.write('    }\n')
            else:
                _out.write(line)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        infile = os.path.join(INLOC, sys.argv[1])
        outfile = os.path.join(OUTLOC, sys.argv[1])
        zetom(infile, outfile)
        print('ready.')
    else:
        print(USAGE)
