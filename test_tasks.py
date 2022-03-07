import pytest
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


def _test_diffconf(monkeypatch, capsys):
    pass


def _test_check_all(monkeypatch, capsys):
    pass


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


def _test_serve(monkeypatch, capsys):
    pass


def _test_start_all(monkeypatch, capsys):
    pass


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
