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
    assert capsys.readouterr().out == "MockContext name {'start': True}\n"
    tasks.start(c)
    assert capsys.readouterr().out == "MockContext None {'start': True}\n"


def test_stop(monkeypatch, capsys):
    def mock_serve(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, '_serve', mock_serve)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.stop(c, 'name')
    assert capsys.readouterr().out == "MockContext name {'stop': True}\n"
    tasks.stop(c)
    assert capsys.readouterr().out == "MockContext None {'stop': True}\n"


def test_restart(monkeypatch, capsys):
    def mock_serve(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, '_serve', mock_serve)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks.restart(c, 'name')
    assert capsys.readouterr().out == "MockContext name {'stop': True, 'start': True}\n"
    tasks.restart(c)
    assert capsys.readouterr().out == "MockContext None {'stop': True, 'start': True}\n"


def test_serve(monkeypatch, capsys):
    def mock_start_all(*args):
        print('call start_all() with args:', *args)
    def mock_restart(*args):
        print('call restart() with args:', *args)
    def mock_serve_django(*args):
        print('call serve_django() with args:', *args)
    def mock_serve_cherry(*args):
        print('call serve_cherry() with args:', *args)
    def mock_serve_plone(*args):
        print('call serve_plone() with args:', *args)
    monkeypatch.setattr(tasks, 'all_names', ['django', 'cherrypy', 'plone', 'name'])
    monkeypatch.setattr(tasks, '_start_all', mock_start_all)
    monkeypatch.setattr(tasks, 'all_django', ['django_server'])
    monkeypatch.setattr(tasks, '_serve_django', mock_serve_django)
    monkeypatch.setattr(tasks, 'all_cherry', ['cherry_server'])
    monkeypatch.setattr(tasks, '_serve_cherry', mock_serve_cherry)
    monkeypatch.setattr(tasks, 'PLONES', ['plone_server'])
    monkeypatch.setattr(tasks, '_serve_plone', mock_serve_plone)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks._serve(c, '', start=True)
    assert capsys.readouterr().out == 'call start_all() with args: MockContext\n'
    tasks._serve(c, 'django,cherrypy,plone', start=True, stop=True)
    assert capsys.readouterr().out == (
            'call serve_django() with args: MockContext django_server True True\n'
            'call serve_cherry() with args: MockContext cherry_server True True\n'
            'call serve_plone() with args: MockContext plone_server True True\n')
    tasks._serve(c, 'django_server', start=True, stop=True)
    assert capsys.readouterr().out == (
            'call serve_django() with args: MockContext django_server True True\n')
    tasks._serve(c, 'cherry_server', start=True, stop=True)
    assert capsys.readouterr().out == (
            'call serve_cherry() with args: MockContext cherry_server True True\n')
    tasks._serve(c, 'plone_server', start=True, stop=True)
    assert capsys.readouterr().out == (
            'call serve_plone() with args: MockContext plone_server True True\n')
    monkeypatch.setattr(tasks, 'all_rst2html', ['srv1', 'srv2'])
    tasks._serve(c, 'rst2html', start=True, stop=True)
    assert capsys.readouterr().out == (
            'call serve_cherry() with args: MockContext srv1 True True\n'
            'call serve_cherry() with args: MockContext srv2 True True\n')
    monkeypatch.setattr(tasks, 'all_names', {'name': tasks.tasks_php})
    tasks._serve(c, '', stop=True)
    assert capsys.readouterr().out == 'unknown server name\nunknown server name\nunknown server name\n'
    monkeypatch.setattr(tasks.tasks_php, 'restart', mock_restart)
    tasks._serve(c, 'name', start=True, stop=True)
    assert capsys.readouterr().out == ('attention: restarting via _serve\n'
                                       'call restart() with args: MockContext\n')


def test_start_all(monkeypatch, capsys):
    def mock_start(c, *args):
        print('called start() with args', args)
    def mock_restart(c, *args):
        print('called restart() with args', args)
    monkeypatch.setattr(tasks, 'all_servers', ['srv1', 'srv2', 'srv3'])
    monkeypatch.setattr(tasks, 'start', mock_start)
    monkeypatch.setattr(tasks, 'restart', mock_restart)
    try:
        os.remove('/tmp/server-srv1-err')
        os.remove('/tmp/server-srv2-err')
    except FileNotFoundError:
        pass
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks._start_all(c)
    assert capsys.readouterr().out == ("starting server srv1\ncalled start() with args ('srv1',)\n"
                                       "starting server srv2\ncalled start() with args ('srv2',)\n"
                                       "starting server srv3\ncalled start() with args ('srv3',)\n")
    with open('/tmp/server-srv1-err', 'w') as f:
        f.write('')
    tasks._start_all(c)
    assert capsys.readouterr().out == ("restarting from srv1\ncalled restart() with args ('srv1',)\n"
                                       "starting server srv2\ncalled start() with args ('srv2',)\n"
                                       "starting server srv3\ncalled start() with args ('srv3',)\n")
    with open('/tmp/server-srv2-err', 'w') as f:
        f.write('')
    tasks._start_all(c)
    assert capsys.readouterr().out == ("restarting from srv2\ncalled restart() with args ('srv2',)\n"
                                       "starting server srv3\ncalled start() with args ('srv3',)\n")


def test_serve_django(monkeypatch, capsys):
    def mock_start_stop(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, 'start_stop', mock_start_stop)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks._serve_django(c, 'name', True, False)
    assert capsys.readouterr().out == "MockContext name True False django {}\n"


def test_serve_cherry(monkeypatch, capsys):
    def mock_start_stop(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, 'start_stop', mock_start_stop)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks._serve_cherry(c, 'name', True, False)
    assert capsys.readouterr().out == "MockContext name True False cherrypy {}\n"


def test_serve_plone(monkeypatch, capsys):
    def mock_start_stop(*args, **kwargs):
        print(*args, kwargs)
    monkeypatch.setattr(tasks, 'start_stop', mock_start_stop)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks._serve_plone(c, 'name', True, False)
    assert capsys.readouterr().out == "MockContext name True False plone {}\n"


def test_start_stop(monkeypatch, capsys):
    class MockModule:
        def start(self, *args):
            print('called start with args', args)
        def stop(self, *args):
            print('called stop with args', args)
    monkeypatch.setattr(tasks, 'all_names', {'type': MockModule})
    c = MockContext()
    tasks.start_stop(c, 'name', True, True, 'type')
    assert capsys.readouterr().out == ("called stop with args ('name',)\n"
                                       "called start with args ('name',)\n")
    tasks.start_stop(c, 'name', False, False, 'type')
    assert not capsys.readouterr().out
