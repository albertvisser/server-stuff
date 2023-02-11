import os
import pytest
from invoke import MockContext
import tasks_django


def mock_run(self, *args, **kwargs):
    print(*args, kwargs)


def mock_get_parms(*args):
    return 'pid', 'sock', ''


def test_start(monkeypatch, capsys):
    def mock_report(*args):
        print('called report_result')
    monkeypatch.setattr(tasks_django, 'django_project_path', {'site': {}, 'stuff': {}})
    monkeypatch.setattr(tasks_django, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(tasks_django, 'report_result', mock_report)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_django.start(c)
    assert capsys.readouterr().out == ('sudo /usr/bin/gunicorn -D -b unix:sock -p pid'
                                       ' site.wsgi:application {}\ncalled report_result\n'
                                       'sudo /usr/bin/gunicorn -D -b unix:sock -p pid'
                                       ' stuff.wsgi:application {}\ncalled report_result\n')
    tasks_django.start(c, 'name')
    assert capsys.readouterr().out == ('sudo /usr/bin/gunicorn -D -b unix:sock -p pid'
                                       ' name.wsgi:application {}\ncalled report_result\n')


def test_stop(monkeypatch, capsys):
    def mock_remove(*args):
        print('called remove_result')
    monkeypatch.setattr(tasks_django, 'django_project_path', {'site': {}, 'stuff': {}})
    monkeypatch.setattr(tasks_django, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(tasks_django, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    if os.path.exists('pid'):
        os.remove('pid')
    tasks_django.stop(c)
    assert not capsys.readouterr().out
    with open('pid', 'w') as out:
        out.write('pid')
    tasks_django.stop(c)
    assert capsys.readouterr().out == ('sudo kill `cat pid` {}\nsudo rm -f pid {}\n'
                                       'called remove_result\n'
                                       'sudo kill `cat pid` {}\nsudo rm -f pid {}\n'
                                       'called remove_result\n')
    tasks_django.stop(c, 'name')
    assert capsys.readouterr().out == ('sudo kill `cat pid` {}\nsudo rm -f pid {}\n'
                                       'called remove_result\n')
    os.remove('pid')


def test_restart(monkeypatch, capsys):
    def mock_stop(*args):
        print('called django.stop')
    def mock_start(*args):
        print('called django.start')
    monkeypatch.setattr(tasks_django, 'django_project_path', {'site': {}, 'stuff': {}})
    monkeypatch.setattr(tasks_django, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(tasks_django, 'start', mock_start)
    monkeypatch.setattr(tasks_django, 'stop', mock_stop)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_django.restart(c)
    assert capsys.readouterr().out == ('called django.stop\ncalled django.start\n'
                                       'called django.stop\ncalled django.start\n')
    tasks_django.restart(c, 'name')
    assert capsys.readouterr().out == 'called django.stop\ncalled django.start\n'


def test_list_servers(monkeypatch, capsys):
    monkeypatch.setattr(tasks_django, 'django_project_path', {'site': {}, 'stuff': {}})
    c = MockContext()
    tasks_django.list_servers(c)
    assert capsys.readouterr().out == 'Available Django projects: site, stuff\n'


def test_get_django_admin_loc(monkeypatch, capsys):
    def mock_run(self, *args, **kwargs):
        return 'start'
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    assert tasks_django.get_django_admin_loc(c) == 'start/contrib/admin/static/admin'


def test_link_admin_css(monkeypatch, capsys, tmp_path):
    def mock_get_parms(*args):
        return 'pid', 'sock', str(tmp_path / 'proj')
    # def mock_run(self, *args, **kwargs):
    #     print(*args, 'in', self.cwd)
    monkeypatch.setattr(tasks_django, 'get_django_admin_loc', lambda x: 'start')
    monkeypatch.setattr(tasks_django, '_get_django_args', mock_get_parms)
    monkeypatch.setattr(tasks_django, 'django_project_path', {'site': {},
                                                              'stuff': {}})
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    projdir = tmp_path / 'proj'
    projdir.mkdir()
    tasks_django.link_admin_css(c)
    assert capsys.readouterr().out == 'ln -s start {}\nln -s start {}\n'
    tasks_django.link_admin_css(c, 'name')
    assert capsys.readouterr().out == 'ln -s start {}\n'
    (projdir / 'static/admin').touch()
    tasks_django.link_admin_css(c, 'name')
    assert capsys.readouterr().out == ''
    (projdir / 'static/admin').unlink()
    (projdir / 'static').rmdir()
    tasks_django.link_admin_css(c, 'name')
    assert capsys.readouterr().out == 'ln -s start {}\n'
    (projdir / 'static').rmdir()
    (projdir / 'static').touch()
    tasks_django.link_admin_css(c, 'name')
    assert capsys.readouterr().out == 'ln -s start {}\n'


def test_get_django_args(monkeypatch):
    monkeypatch.setattr(tasks_django, 'runpath', 'runpath')
    monkeypatch.setattr(tasks_django, 'django_project_path', {'name': 'path_to/name'})
    assert tasks_django._get_django_args('name') == ('runpath/name.pid', 'runpath/name.sock',
                                                     'path_to/name')


def test_get_projectnames(monkeypatch, capsys):
    monkeypatch.setattr(tasks_django, 'django_project_path', {'site': {}, 'stuff': {}})
    assert sorted(tasks_django.get_projectnames()) == ['site', 'stuff']


def test_get_pid(monkeypatch, capsys):
    monkeypatch.setattr(tasks_django, '_get_django_args', mock_get_parms)
    assert tasks_django.get_pid('x') == 'pid'
