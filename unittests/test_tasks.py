import os
import pytest
import types
from invoke import MockContext
import tasks as testee


def mock_run(self, *args):
    print(*args)
    # print('called run with args', args)


def test_addstartup(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'INIT', 'init_loc')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.addstartup(c, 'name')
    assert capsys.readouterr().out == 'sudo chmod +x init_loc/name\nsudo update-rc.d name defaults\n'


def test_editconf(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'EDITORCMD', 'edit {}')
    monkeypatch.setattr(testee, 'get_parms', lambda x: ('pathname', ''))
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.editconf(c, 'name')
    assert capsys.readouterr().out == 'edit pathname\n'


def test_listconf(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'extconf', {'name2': ('path2', True, 'conf'),
                                           'name1': ('path1', False, '@')})
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.listconf(c)
    assert capsys.readouterr().out == ('deployable non-webserver configuration files:\n'
                                       'name1: path1/name1\nname2: path2/conf\n')


def test_modconf(monkeypatch, capsys):
    def mock_modconf(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(testee, 'get_parms', lambda x: ('from', 'to', True))
    monkeypatch.setattr(testee.shared, 'mod_conf', mock_modconf)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.modconf(c, 'name')
    assert capsys.readouterr().out == "MockContext from to {'needs_sudo': True}\n"


def test_modconfb(monkeypatch, capsys):
    def mock_modconf(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(testee, 'get_parms', lambda x: ('from', 'to', True))
    monkeypatch.setattr(testee.shared, 'mod_conf', mock_modconf)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.modconfb(c, 'name')
    assert capsys.readouterr().out == "MockContext from to {'needs_sudo': True, 'backup': True}\n"


def test_modconfa(monkeypatch, capsys):
    def mock_modconf(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(testee, 'get_parms', lambda x: ('from', 'to', True))
    monkeypatch.setattr(testee.shared, 'mod_conf', mock_modconf)
    # monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.modconfa(c, 'name')
    assert capsys.readouterr().out == "MockContext from to {'needs_sudo': True, 'append': True}\n"


def test_get_parms(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'extconf', {'name': ('to', True, 'fname')})
    monkeypatch.setattr(testee, 'HERE', 'here')
    assert testee.get_parms('name') == ('here/misc/fname', 'to', True)
    with pytest.raises(ValueError):
        assert testee.get_parms('noname')


def test_compare(monkeypatch, capsys):
    def mock_diffconf(*args, **kwargs):
        print('called _diffconf with args', args, kwargs)
    monkeypatch.setattr(testee, 'extconf', {'x': 'y', 'a': 'b', 'p': 'q'})
    monkeypatch.setattr(testee, '_diffconf', mock_diffconf)
    c = MockContext()
    testee.compare(c)
    assert capsys.readouterr().out == f"called _diffconf with args ({c}, ['x', 'a', 'p']) {{}}\n"


def test_compareg(monkeypatch, capsys):
    def mock_diffconf(*args, **kwargs):
        print('called _diffconf with args', args, kwargs)
    monkeypatch.setattr(testee, 'extconf', {'x': 'y', 'a': 'b', 'p': 'q'})
    monkeypatch.setattr(testee, '_diffconf', mock_diffconf)
    c = MockContext()
    testee.compareg(c)
    assert capsys.readouterr().out == (f"called _diffconf with args ({c}, ['x', 'a', 'p'])"
                                       " {'gui': True}\n")


def test_diffconf(monkeypatch, capsys, tmp_path):
    def mock_run_2(self, *args, **kwargs):
        print(*args)
        return types.SimpleNamespace(exited=True, stdout='xxx\n')
    def mock_run_3(self, *args, **kwargs):
        print(*args)
        parts = args[0].split(' ')
        return types.SimpleNamespace(exited=False, stdout=f'{parts[2]} {parts[3]}\n')
    testpath = tmp_path / 'server-stuff-test'
    monkeypatch.setattr(testee, 'HERE', str(testpath))
    testpath.mkdir()
    destpath = testpath / 'remote'
    destpath.mkdir()
    miscpath = testpath / 'misc'  # local version (`misc` is hardcoded)
    miscpath.mkdir()
    monkeypatch.setattr(testee, 'extconf', {'name': (f'{destpath}', False, '@'),
                                            'nam2': (f'{destpath}', True, '@')})
    tempdir = '/temp_path'
    monkeypatch.setattr(testee.tempfile, 'mkdtemp', lambda *x: tempdir)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee._diffconf(c, 'name1')
    assert capsys.readouterr().out == f'comparing name skipped: does not exist in {destpath}\n'
    testee._diffconf(c, 'name1,nam2')
    assert capsys.readouterr().out == (f'comparing name skipped: does not exist in {destpath}\n'
                                       f'comparing nam2 skipped: does not exist in {destpath}\n')
    testee._diffconf(c, 'name1')
    assert capsys.readouterr().out == f'comparing name skipped: does not exist in {destpath}\n'
    (destpath / 'name').write_text('')
    (destpath / 'nam2').write_text('')
    (miscpath / 'name').write_text('')
    (miscpath / 'nam2').write_text('')
    testee._diffconf(c, 'name1,nam2', gui=True)
    assert capsys.readouterr().out == (f'sudo cp --no-preserve=mode {destpath}/nam2 {tempdir}/nam2\n'
                                       f'meld {miscpath}/nam2 {tempdir}/nam2\n'
                                       f'meld {miscpath}/name {destpath}/name\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    testee._diffconf(c, 'name1,nam2')
    assert capsys.readouterr().out == (f'sudo cp --no-preserve=mode {destpath}/nam2 {tempdir}/nam2\n'
                                       f'diff -s {miscpath}/nam2 {tempdir}/nam2\n'
                                       'differences for nam2, see /tmp/diff-nam2\n'
                                       f'diff -s {miscpath}/name {destpath}/name\n'
                                       'differences for name, see /tmp/diff-name\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_3)
    c = MockContext()
    testee._diffconf(c, 'name1,nam2')
    assert capsys.readouterr().out == (f'sudo cp --no-preserve=mode {destpath}/nam2 {tempdir}/nam2\n'
                                       f'diff -s {miscpath}/nam2 {tempdir}/nam2\n'
                                       f'{miscpath}/nam2 {destpath}/nam2\n'
                                       f'diff -s {miscpath}/name {destpath}/name\n'
                                       f'{miscpath}/name {destpath}/name\n')


def test_check_all(monkeypatch, capsys):
    def mock_get_pid(arg):
        return '{}_pid'.format(arg)
    def mock_exists(*args):
        return True
    monkeypatch.setattr(testee.tasks_django, 'get_pid', mock_get_pid)
    monkeypatch.setattr(testee, 'all_django', ['django'])
    monkeypatch.setattr(testee, 'all_cherry', ['cherry'])
    monkeypatch.setattr(testee, 'all_other', ['other'])
    monkeypatch.setattr(os.path, 'exists', lambda x: False)
    # monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.check_all(c)
    assert capsys.readouterr().out == ('django: no pid file, server not started or starting failed\n'
                                       'cherry: no pid file, server not started or starting failed\n'
                                       'other: no pid file, server not started or starting failed\n')
    monkeypatch.setattr(os.path, 'exists', lambda x: True)
    testee.check_all(c)
    assert capsys.readouterr().out == ('django: found pid file, server probably started\n'
                                       'cherry: found pid file, server probably started\n'
                                       'other: found pid file, server probably started\n'
                                       'all local servers ok\n')
    testee.check_all(c, 'name')
    assert capsys.readouterr().out == 'all local servers ok\n'


def test_start(monkeypatch, capsys):
    def mock_serve(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(testee, '_serve', mock_serve)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.start(c, 'name')
    assert capsys.readouterr().out == "MockContext name {'start_server': True}\n"
    testee.start(c)
    assert capsys.readouterr().out == "MockContext None {'start_server': True}\n"


def test_stop(monkeypatch, capsys):
    def mock_serve(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(testee, '_serve', mock_serve)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.stop(c, 'name')
    assert capsys.readouterr().out == "MockContext name {'stop_server': True}\n"
    testee.stop(c)
    assert capsys.readouterr().out == "MockContext None {'stop_server': True}\n"


def test_restart(monkeypatch, capsys):
    def mock_serve(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(testee, '_serve', mock_serve)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.restart(c, 'name')
    assert capsys.readouterr().out == "MockContext name {'stop_server': True, 'start_server': True}\n"
    testee.restart(c)
    assert capsys.readouterr().out == "MockContext None {'stop_server': True, 'start_server': True}\n"


def test_serve(monkeypatch, capsys):
    def mock_determine(name):
        print(f'called determine_servertype for `{name}`')
        return name + '_type', False
    def mock_start_stop(c, *args, **kwargs):
        print('called start_stop with args', args, kwargs)
    monkeypatch.setattr(testee, 'start_stop', mock_start_stop)
    monkeypatch.setattr(testee, 'determine_servertype', mock_determine)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee._serve(c, 'x,y')
    assert capsys.readouterr().out == (
            "called determine_servertype for `x`\n"
            "called start_stop with args ('x', False, False, 'x_type') {}\n"
            "called determine_servertype for `y`\n"
            "called start_stop with args ('y', False, False, 'y_type') {}\n")
    testee._serve(c, 'name', True)
    assert capsys.readouterr().out == (
            "called determine_servertype for `name`\n"
            "called start_stop with args ('name', True, False, 'name_type') {}\n")
    testee._serve(c, 'name', True, True)
    assert capsys.readouterr().out == (
            "called determine_servertype for `name`\n"
            "called start_stop with args ('name', True, True, 'name_type') {}\n")
    testee._serve(c, 'name', start_server=True)
    assert capsys.readouterr().out == (
            "called determine_servertype for `name`\n"
            "called start_stop with args ('name', False, True, 'name_type') {}\n")
    monkeypatch.setattr(testee, 'determine_servertype', lambda x: ('', True))
    testee._serve(c, 'name', start_server=True)
    assert capsys.readouterr().out == 'unknown server name `name`\n'
    monkeypatch.setattr(testee, 'servertypes', {'type': {'names': ['x', 'y']}, 'rst2html': {}})
    monkeypatch.setattr(testee, 'determine_servertype', lambda x: (x, True))
    testee._serve(c, '', start_server=True)
    assert capsys.readouterr().out == ("called start_stop with args ('x', False, True, 'type') {}\n"
                                       "called start_stop with args ('y', False, True, 'type') {}\n")


def test_determine_servertype(monkeypatch):
    mock_servertypes = {'group': {'names': ['1', '2'],
                                  'handler': 'handler_module'}}
    monkeypatch.setattr(testee, 'servertypes', mock_servertypes)
    assert testee.determine_servertype('group') == ('group', True)
    assert testee.determine_servertype('1') == ('group', False)
    assert testee.determine_servertype('5') == ('', False)


def test_start_stop(monkeypatch, capsys):
    class MockModule:
        def start(self, *args):
            print('called start with args', args)
        def stop(self, *args):
            print('called stop with args', args)
    monkeypatch.setattr(testee, 'servertypes', {'type': {'names': ['name'], 'handler': MockModule}})
    monkeypatch.setattr(testee, 'all_names', {'type': MockModule})
    c = MockContext()
    testee.start_stop(c, 'name', True, True, 'type')
    assert capsys.readouterr().out == ("called stop with args ()\n"
                                       "called start with args ()\n")
    testee.start_stop(c, 'name', False, False, 'type')
    assert not capsys.readouterr().out
    monkeypatch.setattr(testee, 'servertypes', {'type': {'names': ['name', 'name2'],
                                                        'handler': MockModule}})
    testee.start_stop(c, 'name', True, True, 'type')
    assert capsys.readouterr().out == ("called stop with args ('name',)\n"
                                       "called start with args ('name',)\n")
