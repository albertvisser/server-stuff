"""unittests for ./tasks_cherrypy.py
"""
import os
import pytest
from invoke import MockContext
import tasks_cherrypy
mock_allproj = ('all', 'proj')


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def mock_get_parms(*args):
    """stub for tasks_cherrypy._get_cherry_parms
    """
    return 'conf', 'pad', 'prog', 'pid', 'sock'


def test_start(monkeypatch, capsys):
    """unittest for tasks_cherrypy.start
    """
    def mock_report(*args):
        """stub
        """
        print('called report_result')
    monkeypatch.setattr(tasks_cherrypy, 'allproj', mock_allproj)
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
    """unittest for tasks_cherrypy.stop
    """
    def mock_remove(*args):
        """stub
        """
        print('called remove_result')
    monkeypatch.setattr(tasks_cherrypy, 'allproj', mock_allproj)
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
    """unittest for tasks_cherrypy.restart
    """
    def mock_stop(*args):
        """stub
        """
        print('called cherrypy.stop')
    def mock_start(*args):
        """stub
        """
        print('called cherrypy.start')
    monkeypatch.setattr(tasks_cherrypy, 'allproj', mock_allproj)
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
    """unittest for tasks_cherrypy.list_servers
    """
    monkeypatch.setattr(tasks_cherrypy, 'allproj', mock_allproj)
    monkeypatch.setattr(tasks_cherrypy, '_get_cherry_parms', mock_get_parms)
    c = MockContext()
    tasks_cherrypy.list_servers(c)
    assert capsys.readouterr().out == 'Available CherryPy projects: all, proj\n'


def test_get_parms(monkeypatch):
    """unittest for tasks_cherrypy.get_parms
    """
    with pytest.raises(TypeError):
        tasks_cherrypy._get_cherry_parms()
    monkeypatch.setattr(tasks_cherrypy, 'allproj', ['name_test', 'other', 'project-2'])
    assert tasks_cherrypy._get_cherry_parms('name_stuff') == ('name_stuff.conf',
                                                              '/home/albert/projects/name',
                                                              'start_name_stuff',
                                                              '/var/run/name_stuff.pid',
                                                              '/var/run/name_stuff.sock')
    assert tasks_cherrypy._get_cherry_parms('other') == ('other.conf',
                                                         '/home/albert/projects/other',
                                                         'start_other',
                                                         '/var/run/other.pid',
                                                         '/var/run/other.sock')
    assert tasks_cherrypy._get_cherry_parms('project-2') == ('project.conf',
                                                             '/home/albert/projects/.frozen/project-2',
                                                             'start_project',
                                                             '/var/run/projectc.pid',
                                                             '/var/run/projectc.sock')


def test_get_projectnames(monkeypatch):
    """unittest for tasks_cherrypy.get_projectnames
    """
    monkeypatch.setattr(tasks_cherrypy, 'allproj', mock_allproj)
    assert tasks_cherrypy.get_projectnames() == ('all', 'proj')


def test_get_pid(monkeypatch):
    """unittest for tasks_cherrypy.get_pid
    """
    monkeypatch.setattr(tasks_cherrypy, '_get_cherry_parms', mock_get_parms)
    assert tasks_cherrypy.get_pid('name') == 'pid'
