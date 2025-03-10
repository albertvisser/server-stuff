"""unittests for ./tasks_django.py
"""
import os
import types
from invoke import MockContext
import tasks_django as testee


def mock_run(self, *args, **kwargs):
    """stub for invoke.Context.run
    """
    print(*args, kwargs)


def mock_get_parms(*args):
    """stub for tasks_django._get_django_args
    """
    return 'pid', 'sock', ''


def test_start(monkeypatch, capsys):
    """unittest for tasks_django.start
    """
    def mock_check(*args):
        """stub
        """
        print('called check_result')
        return 'xxx'
    def mock_check_2(*args):
        """stub
        """
        print('called check_result')
        return ''
    def mock_report(*args):
        """stub
        """
        print('called report_result')
    monkeypatch.setattr(testee, 'django_project_path', {'site': {}, 'stuff': {}})
    monkeypatch.setattr(testee, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(testee, 'check_result', mock_check)
    monkeypatch.setattr(testee, 'report_result', mock_report)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.start(c)
    assert capsys.readouterr().out == ('called check_result\nsite xxx\n'
                                       'called check_result\nstuff xxx\n')
    monkeypatch.setattr(testee, 'check_result', mock_check_2)
    testee.start(c)
    assert capsys.readouterr().out == ('called check_result\n'
                                       'sudo /usr/bin/gunicorn -D -b unix:sock -p pid'
                                       ' site.wsgi:application {}\n'
                                       'called report_result\n'
                                       'called check_result\n'
                                       'sudo /usr/bin/gunicorn -D -b unix:sock -p pid'
                                       ' stuff.wsgi:application {}\n'
                                       'called report_result\n')
    monkeypatch.setattr(testee, 'check_result', mock_check)
    testee.start(c, 'name')
    assert capsys.readouterr().out == 'called check_result\nname xxx\n'
    monkeypatch.setattr(testee, 'check_result', mock_check_2)
    testee.start(c, 'name')
    assert capsys.readouterr().out == ('called check_result\n'
                                       'sudo /usr/bin/gunicorn -D -b unix:sock -p pid'
                                       ' name.wsgi:application {}\n'
                                       'called report_result\n')


def test_stop(monkeypatch, capsys):
    """unittest for tasks_django.stop
    """
    def mock_remove(*args):
        """stub
        """
        print('called remove_result')
    monkeypatch.setattr(testee, 'django_project_path', {'site': {}, 'stuff': {}})
    monkeypatch.setattr(testee, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(testee, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    if os.path.exists('pid'):
        os.remove('pid')
    testee.stop(c)
    assert not capsys.readouterr().out
    with open('pid', 'w') as out:
        out.write('pid')
    testee.stop(c)
    assert capsys.readouterr().out == ('sudo kill `cat pid` {}\nsudo rm -f pid {}\n'
                                       'called remove_result\n'
                                       'sudo kill `cat pid` {}\nsudo rm -f pid {}\n'
                                       'called remove_result\n')
    testee.stop(c, 'name')
    assert capsys.readouterr().out == ('sudo kill `cat pid` {}\nsudo rm -f pid {}\n'
                                       'called remove_result\n')
    os.remove('pid')


def test_restart(monkeypatch, capsys):
    """unittest for tasks_django.restart
    """
    def mock_stop(*args):
        """stub
        """
        print('called django.stop')
    def mock_start(*args):
        """stub
        """
        print('called django.start')
    monkeypatch.setattr(testee, 'django_project_path', {'site': {}, 'stuff': {}})
    monkeypatch.setattr(testee, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(testee, 'start', mock_start)
    monkeypatch.setattr(testee, 'stop', mock_stop)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.restart(c)
    assert capsys.readouterr().out == ('called django.stop\ncalled django.start\n'
                                       'called django.stop\ncalled django.start\n')
    testee.restart(c, 'name')
    assert capsys.readouterr().out == 'called django.stop\ncalled django.start\n'


def test_list_servers(monkeypatch, capsys):
    """unittest for tasks_django.list_servers
    """
    monkeypatch.setattr(testee, 'django_project_path', {'site': {}, 'stuff': {}})
    c = MockContext()
    testee.list_servers(c)
    assert capsys.readouterr().out == 'Available Django projects: site, stuff\n'


def test_get_django_admin_loc(monkeypatch):
    """unittest for tasks_django.get_django_admin_loc
    """
    def mock_run(self, *args, **kwargs):
        """stub
        """
        return types.SimpleNamespace(stdout="['start']")
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert testee.get_django_admin_loc(c) == 'start/contrib/admin/static/admin'


def test_link_admin_css(monkeypatch, capsys, tmp_path):
    """unittest for tasks_django.link_admin_css
    """
    def mock_get_parms(*args):
        """stub
        """
        return 'pid', 'sock', str(tmp_path / 'proj')
    monkeypatch.setattr(testee, 'get_django_admin_loc', lambda x: 'start')
    monkeypatch.setattr(testee, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(testee, 'django_project_path', {'site': {}, 'stuff': {}})
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    projdir = tmp_path / 'proj'
    projdir.mkdir()
    testee.link_admin_css(c)
    assert capsys.readouterr().out == 'ln -s start {}\nln -s start {}\n'
    testee.link_admin_css(c, 'name')
    assert capsys.readouterr().out == 'ln -s start {}\n'
    (projdir / 'static/admin').touch()
    testee.link_admin_css(c, 'name')
    assert capsys.readouterr().out == ''
    testee.link_admin_css(c, 'name', force=True)
    assert capsys.readouterr().out == 'ln -s start {}\n'
    # (projdir / 'static/admin').unlink() is al verwijderd door de voorgaande test
    (projdir / 'static').rmdir()
    testee.link_admin_css(c, 'name')
    assert capsys.readouterr().out == 'ln -s start {}\n'
    (projdir / 'static').rmdir()
    (projdir / 'static').touch()
    testee.link_admin_css(c, 'name')
    assert capsys.readouterr().out == 'ln -s start {}\n'


def test_check_admin_links(monkeypatch, capsys, tmp_path):
    """unittest for tasks_django.check_admin_links
    """
    def mock_get_parms(*args):
        """stub
        """
        return 'pid', 'sock', str(tmp_path / 'proj')
    monkeypatch.setattr(testee, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(testee, 'django_project_path', {'site': {}})
    monkeypatch.setattr(MockContext, 'run', mock_run)
    # monkeypatch.setattr(testee.os.path, 'exists', lambda *x: True)
    # monkeypatch.setattr(testee.os.path, 'islink', lambda *x: True)
    c = MockContext()
    projdir = tmp_path / 'proj'
    projdir.mkdir()
    (projdir / 'test').touch()
    (projdir / 'static').mkdir()
    (projdir / 'static' / 'admin').symlink_to(projdir / 'test')
    monkeypatch.setattr(testee, 'get_django_admin_loc', lambda x: str(projdir / 'test'))
    testee.check_admin_links(c)
    assert capsys.readouterr().out == (
            'For project site:\n'
            f"  looking for {projdir / 'static' / 'admin'}\n"
            f"  symlink found pointing to {projdir / 'test'}, all is well.\n")
    monkeypatch.setattr(testee, 'get_django_admin_loc', lambda x: 'start')
    testee.check_admin_links(c)
    assert capsys.readouterr().out == (
            'For project site:\n'
            f"  looking for {projdir / 'static' / 'admin'}\n"
            f"  symlink found pointing to {projdir / 'test'}, removing and creating new symlink\n"
            'ln -s start {}\n')
    (projdir / 'static' / 'admin').symlink_to('xyzoyyughju')
    testee.check_admin_links(c)
    assert capsys.readouterr().out == (
            'For project site:\n'
            f"  looking for {projdir / 'static' / 'admin'}\n"
            f"  symlink found pointing to invalid location, removing and creating new symlink\n"
            'ln -s start {}\n')

    (projdir / 'static' / 'admin').touch()
    # monkeypatch.setattr(testee.os.path, 'islink', lambda *x: False)
    testee.check_admin_links(c)
    assert capsys.readouterr().out == (
            'For project site:\n'
            f"  looking for {projdir / 'static' / 'admin'}\n"
            "  admin found but not a symlink, renaming and creating new symlink\n"
            'ln -s start {}\n')
    # (projdir / 'static' / 'admin').unlink()
    # monkeypatch.setattr(testee.os.path, 'islink', lambda *x: False)
    testee.check_admin_links(c)
    assert capsys.readouterr().out == (
            'For project site:\n'
            f"  looking for {projdir / 'static' / 'admin'}\n"
            '  no admin found, creating new symlink\n'
            'ln -s start {}\n')


def test_get_django_args(monkeypatch):
    """unittest for tasks_django.get_django_args
    """
    monkeypatch.setattr(testee, 'runpath', 'runpath')
    monkeypatch.setattr(testee, 'django_project_path', {'name': 'path_to/name'})
    assert testee._get_django_args('name') == ('runpath/name.pid', 'runpath/name.sock',
                                               'path_to/name')


def test_get_projectnames(monkeypatch):
    """unittest for tasks_django.get_projectnames
    """
    monkeypatch.setattr(testee, 'django_project_path', {'site': {}, 'stuff': {}})
    assert sorted(testee.get_projectnames()) == ['site', 'stuff']


def test_get_pid(monkeypatch):
    """unittest for tasks_django.get_pid
    """
    monkeypatch.setattr(testee, '_get_django_args', mock_get_parms)
    assert testee.get_pid('x') == 'pid'
