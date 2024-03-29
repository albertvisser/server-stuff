"""unittests for ./tasks_trac.py
"""
from invoke import MockContext
import tasks_trac


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def test_start(monkeypatch, capsys):
    """unittest for tasks_trac.start
    """
    def mock_report(*args):
        """stub
        """
        print('called report_result')
    monkeypatch.setattr(tasks_trac, 'trac_pid', 'pid')
    monkeypatch.setattr(tasks_trac, 'trac_sock', 'socket')
    monkeypatch.setattr(tasks_trac, 'report_result', mock_report)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_trac.start(c)
    assert capsys.readouterr().out == ('sudo /usr/bin/gunicorn -D -b unix:socket -p pid '
                                       'tracwsgi:application\ncalled report_result\n')


def test_stop(monkeypatch, capsys):
    """unittest for tasks_trac.stop
    """
    def mock_remove(*args):
        """stub
        """
        print('called remove_result')
    monkeypatch.setattr(tasks_trac, 'trac_pid', 'pid')
    monkeypatch.setattr(tasks_trac, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_trac.stop(c)
    assert capsys.readouterr().out == 'sudo kill `cat pid`\nsudo rm -f pid\ncalled remove_result\n'


def test_restart(monkeypatch, capsys):
    """unittest for tasks_trac.restart
    """
    def mock_start(*args):
        """stub
        """
        print('called trac_start')
    def mock_stop(*args):
        """stub
        """
        print('called trac_stop')
    monkeypatch.setattr(tasks_trac, 'start', mock_start)
    monkeypatch.setattr(tasks_trac, 'stop', mock_stop)
    c = MockContext()
    tasks_trac.restart(c)
    assert capsys.readouterr().out == 'called trac_stop\ncalled trac_start\n'


def test_editconf(monkeypatch, capsys):
    """unittest for tasks_trac.editconf
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_trac.editconf(c)
    assert capsys.readouterr().out == 'fabsrv editconf trac\n'


def test_modconf(monkeypatch, capsys):
    """unittest for tasks_trac.modconf
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_trac.modconf(c)
    assert capsys.readouterr().out == 'fabsrv modconf -n trac\n'
