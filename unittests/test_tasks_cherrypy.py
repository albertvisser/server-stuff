"""unittests for ./testee.py
"""
import os
import pytest
from invoke import MockContext
import tasks_cherrypy as testee
mock_allproj = ('all', 'proj')


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def mock_get_parms(*args):
    """stub for testee._get_cherry_parms
    """
    return 'conf', 'pad', 'prog', 'pid', 'sock'


def test_start(monkeypatch, capsys):
    """unittest for testee.start
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
    monkeypatch.setattr(testee, 'allproj', mock_allproj)
    monkeypatch.setattr(testee, '_get_cherry_parms', mock_get_parms)
    monkeypatch.setattr(testee, 'check_result', mock_check)
    monkeypatch.setattr(testee, 'report_result', mock_report)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.start(c)
    assert capsys.readouterr().out == 'called check_result\nall xxx\ncalled check_result\nproj xxx\n'
    monkeypatch.setattr(testee, 'check_result', mock_check_2)
    testee.start(c)
    assert capsys.readouterr().out == ('called check_result\n'
                                       'sudo /usr/bin/cherryd -c conf -d -p pid -i prog\n'
                                       'called report_result\n'
                                       'called check_result\n'
                                       'sudo /usr/bin/cherryd -c conf -d -p pid -i prog\n'
                                       'called report_result\n')
    monkeypatch.setattr(testee, 'check_result', mock_check)
    testee.start(c, 'name')
    assert capsys.readouterr().out == 'called check_result\nname xxx\n'
    monkeypatch.setattr(testee, 'check_result', mock_check_2)
    testee.start(c, 'name')
    assert capsys.readouterr().out == ('called check_result\n'
                                       'sudo /usr/bin/cherryd -c conf -d -p pid -i prog\n'
                                       'called report_result\n')


def test_stop(monkeypatch, capsys):
    """unittest for testee.stop
    """
    def mock_remove(*args):
        """stub
        """
        print('called remove_result')
    monkeypatch.setattr(testee, 'allproj', mock_allproj)
    monkeypatch.setattr(testee, '_get_cherry_parms', mock_get_parms)
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
    assert capsys.readouterr().out == ('sudo kill -s SIGKILL `cat pid`\nsudo rm -f pid\n'
                                       'called remove_result\n'
                                       'sudo kill -s SIGKILL `cat pid`\nsudo rm -f pid\n'
                                       'called remove_result\n')
    testee.stop(c, 'name')
    assert capsys.readouterr().out == ('sudo kill -s SIGKILL `cat pid`\nsudo rm -f pid\n'
                                       'called remove_result\n')
    os.remove('pid')


def test_restart(monkeypatch, capsys):
    """unittest for testee.restart
    """
    def mock_stop(*args):
        """stub
        """
        print('called cherrypy.stop')
    def mock_start(*args):
        """stub
        """
        print('called cherrypy.start')
    monkeypatch.setattr(testee, 'allproj', mock_allproj)
    monkeypatch.setattr(testee, '_get_cherry_parms', mock_get_parms)
    monkeypatch.setattr(testee, 'start', mock_start)
    monkeypatch.setattr(testee, 'stop', mock_stop)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.restart(c)
    assert capsys.readouterr().out == ('called cherrypy.stop\ncalled cherrypy.start\n'
                                       'called cherrypy.stop\ncalled cherrypy.start\n')
    testee.restart(c, 'name')
    assert capsys.readouterr().out == 'called cherrypy.stop\ncalled cherrypy.start\n'


def test_list_servers(monkeypatch, capsys):
    """unittest for testee.list_servers
    """
    monkeypatch.setattr(testee, 'allproj', mock_allproj)
    monkeypatch.setattr(testee, '_get_cherry_parms', mock_get_parms)
    c = MockContext()
    testee.list_servers(c)
    assert capsys.readouterr().out == 'Available CherryPy projects: all, proj\n'


def test_get_parms(monkeypatch):
    """unittest for testee.get_parms
    """
    with pytest.raises(TypeError):
        testee._get_cherry_parms()
    monkeypatch.setattr(testee, 'allproj', ['name_test', 'other', 'project-2'])
    assert testee._get_cherry_parms('name_stuff') == ('name_stuff.conf',
                                                              '/home/albert/projects/name',
                                                              'start_name_stuff',
                                                              '/var/run/name_stuff.pid',
                                                              '/var/run/name_stuff.sock')
    assert testee._get_cherry_parms('other') == ('other.conf',
                                                         '/home/albert/projects/other',
                                                         'start_other',
                                                         '/var/run/other.pid',
                                                         '/var/run/other.sock')
    assert testee._get_cherry_parms('project-2') == ('project.conf',
                                                             '/home/albert/projects/.frozen/project-2',
                                                             'start_project',
                                                             '/var/run/projectc.pid',
                                                             '/var/run/projectc.sock')


def test_get_projectnames(monkeypatch):
    """unittest for testee.get_projectnames
    """
    monkeypatch.setattr(testee, 'allproj', mock_allproj)
    assert testee.get_projectnames() == ('all', 'proj')


def test_get_pid(monkeypatch):
    """unittest for testee.get_pid
    """
    monkeypatch.setattr(testee, '_get_cherry_parms', mock_get_parms)
    assert testee.get_pid('name') == 'pid'
