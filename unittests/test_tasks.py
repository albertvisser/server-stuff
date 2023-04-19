import os
import pytest
import types
from invoke import MockContext
import tasks


def mock_run(self, *args):
    print(*args)


def test_addstartup(monkeypatch, capsys):
    monkeypatch.setattr(tasks, 'INIT', 'init_loc')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks.addstartup(c, 'name')
    assert capsys.readouterr().out == 'sudo chmod +x init_loc/name\nsudo update-rc.d name defaults\n'


def test_editconf(monkeypatch, capsys):
    monkeypatch.setattr(tasks, 'EDITORCMD', 'edit {}')
    monkeypatch.setattr(tasks, 'get_parms', lambda x: ('pathname', ''))
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks.editconf(c, 'name')
    assert capsys.readouterr().out == 'edit pathname\n'


def test_listconf(monkeypatch, capsys):
    monkeypatch.setattr(tasks, 'extconf', {'name2': ('path2', True, 'conf'),
                                           'name1': ('path1', False, '@')})
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks.listconf(c)
    assert capsys.readouterr().out == ('deployable non-webserver configuration files:\n'
                                       'name1: path1/name1\nname2: path2/conf\n')


def test_modconf(monkeypatch, capsys):
    def mock_modconf(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, 'get_parms', lambda x: ('from', 'to', True))
    monkeypatch.setattr(tasks.shared, 'mod_conf', mock_modconf)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.modconf(c, 'name')
    assert capsys.readouterr().out == "MockContext from to {'needs_sudo': True}\n"


def test_modconfb(monkeypatch, capsys):
    def mock_modconf(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, 'get_parms', lambda x: ('from', 'to', True))
    monkeypatch.setattr(tasks.shared, 'mod_conf', mock_modconf)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.modconfb(c, 'name')
    assert capsys.readouterr().out == "MockContext from to {'needs_sudo': True, 'backup': True}\n"


def test_modconfa(monkeypatch, capsys):
    def mock_modconf(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, 'get_parms', lambda x: ('from', 'to', True))
    monkeypatch.setattr(tasks.shared, 'mod_conf', mock_modconf)
    # monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.modconfa(c, 'name')
    assert capsys.readouterr().out == "MockContext from to {'needs_sudo': True, 'append': True}\n"


def test_get_parms(monkeypatch, capsys):
    monkeypatch.setattr(tasks, 'extconf', {'name': ('to', True, 'fname')})
    monkeypatch.setattr(tasks, 'HERE', 'here')
    assert tasks.get_parms('name') == ('here/misc/fname', 'to', True)
    with pytest.raises(ValueError):
        assert tasks.get_parms('noname')


def test_compare(monkeypatch, capsys):
    def mock_diffconf(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, '_diffconf', mock_diffconf)
    # monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.compare(c)
    assert capsys.readouterr().out == 'MockContext {}\n'


def test_compareg(monkeypatch, capsys):
    def mock_diffconf(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, '_diffconf', mock_diffconf)
    # monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.compareg(c)
    assert capsys.readouterr().out == "MockContext {'gui': True}\n"


def test_diffconf(monkeypatch, capsys, tmp_path):
    def mock_run_2(self, *args, **kwargs):
        print(*args)
        return types.SimpleNamespace(exited=True, stdout='differences')
    def mock_run_3(self, *args, **kwargs):
        print(*args)
        return types.SimpleNamespace(exited=False, stdout='differences')
    testpath = tmp_path / 'server-stuff-test'
    monkeypatch.setattr(tasks, 'HERE', str(testpath))
    testpath.mkdir()
    destpath = testpath / 'to'
    destpath.mkdir()
    miscpath = testpath / 'misc'
    miscpath.mkdir()
    monkeypatch.setattr(tasks, 'extconf', {'name': (f'{destpath}', True, '@')})
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks._diffconf(c)
    assert capsys.readouterr().out == (f'comparing name skipped: does not exist in {destpath}\n')
    (destpath / 'name').write_text('')
    (miscpath / 'name').write_text('')
    tasks._diffconf(c, gui=True)
    assert capsys.readouterr().out == f'meld {miscpath}/name {destpath}/name\n'
    monkeypatch.setattr(MockContext, 'run', mock_run_2)
    c = MockContext()
    tasks._diffconf(c)
    assert capsys.readouterr().out == (f'diff -s {miscpath}/name {destpath}/name\n'
                                       'differences for name, see /tmp/diff-name\n')
    monkeypatch.setattr(MockContext, 'run', mock_run_3)
    c = MockContext()
    tasks._diffconf(c)
    assert capsys.readouterr().out == (f'diff -s {miscpath}/name {destpath}/name\n'
                                       'differences')


def test_check_all(monkeypatch, capsys):
    def mock_get_pid(arg):
        return '{}_pid'.format(arg)
    def mock_exists(*args):
        return True
    monkeypatch.setattr(tasks.tasks_django, 'get_pid', mock_get_pid)
    monkeypatch.setattr(tasks, 'all_django', ['django'])
    monkeypatch.setattr(tasks, 'all_cherry', ['cherry'])
    monkeypatch.setattr(tasks, 'all_other', ['other'])
    monkeypatch.setattr(os.path, 'exists', lambda x: False)
    # monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.check_all(c)
    assert capsys.readouterr().out == ('django: no pid file, server not started or starting failed\n'
                                       'cherry: no pid file, server not started or starting failed\n'
                                       'other: no pid file, server not started or starting failed\n')
    monkeypatch.setattr(os.path, 'exists', lambda x: True)
    tasks.check_all(c)
    assert capsys.readouterr().out == ('django: found pid file, server probably started\n'
                                       'cherry: found pid file, server probably started\n'
                                       'other: found pid file, server probably started\n'
                                       'all local servers ok\n')
    tasks.check_all(c, 'name')
    assert capsys.readouterr().out == 'all local servers ok\n'


def test_start(monkeypatch, capsys):
    def mock_serve(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, '_serve', mock_serve)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.start(c, 'name')
    assert capsys.readouterr().out == "MockContext name {'start_server': True}\n"
    tasks.start(c)
    assert capsys.readouterr().out == "MockContext None {'start_server': True}\n"


def test_stop(monkeypatch, capsys):
    def mock_serve(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, '_serve', mock_serve)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.stop(c, 'name')
    assert capsys.readouterr().out == "MockContext name {'stop_server': True}\n"
    tasks.stop(c)
    assert capsys.readouterr().out == "MockContext None {'stop_server': True}\n"


def test_restart(monkeypatch, capsys):
    def mock_serve(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, '_serve', mock_serve)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.restart(c, 'name')
    assert capsys.readouterr().out == "MockContext name {'stop_server': True, 'start_server': True}\n"
    tasks.restart(c)
    assert capsys.readouterr().out == "MockContext None {'stop_server': True, 'start_server': True}\n"


def test_serve(monkeypatch, capsys):
    def mock_determine(name):
        print(f'called determine_servertype for `{name}`')
        return name + '_type', False
    def mock_start_stop(c, *args, **kwargs):
        print('called start_stop with args', args, kwargs)
    monkeypatch.setattr(tasks, 'start_stop', mock_start_stop)
    monkeypatch.setattr(tasks, 'determine_servertype', mock_determine)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks._serve(c, 'x,y')
    assert capsys.readouterr().out == (
            "called determine_servertype for `x`\n"
            "called start_stop with args ('x', False, False, 'x_type') {}\n"
            "called determine_servertype for `y`\n"
            "called start_stop with args ('y', False, False, 'y_type') {}\n")
    tasks._serve(c, 'name', True)
    assert capsys.readouterr().out == (
            "called determine_servertype for `name`\n"
            "called start_stop with args ('name', True, False, 'name_type') {}\n")
    tasks._serve(c, 'name', True, True)
    assert capsys.readouterr().out == (
            "called determine_servertype for `name`\n"
            "called start_stop with args ('name', True, True, 'name_type') {}\n")
    tasks._serve(c, 'name', start_server=True)
    assert capsys.readouterr().out == (
            "called determine_servertype for `name`\n"
            "called start_stop with args ('name', False, True, 'name_type') {}\n")
    monkeypatch.setattr(tasks, 'determine_servertype', lambda x: ('', True))
    tasks._serve(c, 'name', start_server=True)
    assert capsys.readouterr().out == 'unknown server name `name`\n'
    monkeypatch.setattr(tasks, 'servertypes', {'type': {'names': ['x', 'y']}, 'rst2html': {}})
    monkeypatch.setattr(tasks, 'determine_servertype', lambda x: (x, True))
    tasks._serve(c, '', start_server=True)
    assert capsys.readouterr().out == ("called start_stop with args ('x', False, True, 'type') {}\n"
                                       "called start_stop with args ('y', False, True, 'type') {}\n")


def test_determine_servertype(monkeypatch):
    mock_servertypes = {'group': {'names': ['1', '2'],
                                  'handler': 'handler_module'}}
    monkeypatch.setattr(tasks, 'servertypes', mock_servertypes)
    assert tasks.determine_servertype('group') == ('group', True)
    assert tasks.determine_servertype('1') == ('group', False)
    assert tasks.determine_servertype('5') == ('', False)


def test_start_stop(monkeypatch, capsys):
    class MockModule:
        def start(self, *args):
            print('called start with args', args)
        def stop(self, *args):
            print('called stop with args', args)
    monkeypatch.setattr(tasks, 'servertypes', {'type': {'names': ['name'], 'handler': MockModule}})
    monkeypatch.setattr(tasks, 'all_names', {'type': MockModule})
    c = MockContext()
    tasks.start_stop(c, 'name', True, True, 'type')
    assert capsys.readouterr().out == ("called stop with args ()\n"
                                       "called start with args ()\n")
    tasks.start_stop(c, 'name', False, False, 'type')
    assert not capsys.readouterr().out
    monkeypatch.setattr(tasks, 'servertypes', {'type': {'names': ['name', 'name2'],
                                                        'handler': MockModule}})
    tasks.start_stop(c, 'name', True, True, 'type')
    assert capsys.readouterr().out == ("called stop with args ('name',)\n"
                                       "called start with args ('name',)\n")
