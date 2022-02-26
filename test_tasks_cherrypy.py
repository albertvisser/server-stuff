import os
import pytest
from invoke import MockContext
import tasks_cherrypy


def mock_run(self, *args):
    print(*args)


def mock_get_parms(*args):
    if args:
        return 'conf', 'pad', 'prog', 'pid', 'sock'
    return 'all', 'proj'


def test_start(monkeypatch, capsys):
    def mock_report(*args):
        print('called report_result')
    monkeypatch.setattr(tasks_cherrypy, '_get_cherry_parms', mock_get_parms)
    monkeypatch.setattr(tasks_cherrypy, 'report_result', mock_report)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_cherrypy.start(c)
    assert capsys.readouterr().out == ('sudo /usr/bin/cherryd -c conf -d -p pid -i prog\n'
                                       'called report_result\n'
                                       'sudo /usr/bin/cherryd -c conf -d -p pid -i prog\n'
                                       'called report_result\n')
    tasks_cherrypy.start(c, 'name')
    assert capsys.readouterr().out == ('sudo /usr/bin/cherryd -c conf -d -p pid -i prog\n'
                                       'called report_result\n')


def test_stop(monkeypatch, capsys):
    def mock_remove(*args):
        print('called remove_result')
    monkeypatch.setattr(tasks_cherrypy, '_get_cherry_parms', mock_get_parms)
    monkeypatch.setattr(tasks_cherrypy, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    if os.path.exists('pid'):
        os.remove('pid')
    tasks_cherrypy.stop(c)
    assert not capsys.readouterr().out
    with open('pid', 'w') as out:
        out.write('pid')
    tasks_cherrypy.stop(c)
    assert capsys.readouterr().out == ('sudo kill -s SIGKILL `cat pid`\nsudo rm -f pid\n'
                                       'called remove_result\n'
                                       'sudo kill -s SIGKILL `cat pid`\nsudo rm -f pid\n'
                                       'called remove_result\n')
    tasks_cherrypy.stop(c, 'name')
    assert capsys.readouterr().out == ('sudo kill -s SIGKILL `cat pid`\nsudo rm -f pid\n'
                                       'called remove_result\n')
    os.remove('pid')


def test_restart(monkeypatch, capsys):
    def mock_stop(*args):
        print('called cherrypy.stop')
    def mock_start(*args):
        print('called cherrypy.start')
    monkeypatch.setattr(tasks_cherrypy, '_get_cherry_parms', mock_get_parms)
    monkeypatch.setattr(tasks_cherrypy, 'start', mock_start)
    monkeypatch.setattr(tasks_cherrypy, 'stop', mock_stop)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_cherrypy.restart(c)
    assert capsys.readouterr().out == ('called cherrypy.stop\ncalled cherrypy.start\n'
                                       'called cherrypy.stop\ncalled cherrypy.start\n')
    tasks_cherrypy.restart(c, 'name')
    assert capsys.readouterr().out == 'called cherrypy.stop\ncalled cherrypy.start\n'


def test_list_servers(monkeypatch, capsys):
    monkeypatch.setattr(tasks_cherrypy, '_get_cherry_parms', mock_get_parms)
    c = MockContext()
    tasks_cherrypy.list_servers(c)
    assert capsys.readouterr().out == 'Available CherryPy projects: all, proj\n'


def test_get_parms(monkeypatch, capsys):
    monkeypatch.setattr(tasks_cherrypy, 'allproj', 'gargl')
    assert tasks_cherrypy._get_cherry_parms() == 'gargl'


def test_get_projectnames(monkeypatch):
    monkeypatch.setattr(tasks_cherrypy, 'allproj', 'gargl')
    assert tasks_cherrypy.get_projectnames() == 'gargl'


def test_get_pid(monkeypatch):
    monkeypatch.setattr(tasks_cherrypy, '_get_cherry_parms', mock_get_parms)
    assert tasks_cherrypy.get_pid('name') == 'pid'
