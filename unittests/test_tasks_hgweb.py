"""unittests for ./tasks_hgweb.py
"""
from invoke import MockContext
import tasks_hgweb


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def test_start(monkeypatch, capsys):
    """unittest for tasks_hgweb.start
    """
    def mock_report(*args):
        """stub
        """
        print('called report_result()')
    tasks_hgweb.HGWEB = 'here'
    tasks_hgweb.hgweb_pid = 'pid'
    tasks_hgweb.hgweb_sock = 'socket'
    monkeypatch.setattr(tasks_hgweb, 'report_result', mock_report)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_hgweb.start(c)
    assert capsys.readouterr().out == ('sudo spawn-fcgi -f here/hgweb.fcgi -s socket -P pid'
                                       ' -u www-data\ncalled report_result()\n')


def test_stop(monkeypatch, capsys):
    """unittest for tasks_hgweb.stop
    """
    def mock_remove(*args):
        """stub
        """
        print('called remove_result()')
    tasks_hgweb.hgweb_pid = 'pid'
    monkeypatch.setattr(tasks_hgweb, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_hgweb.stop(c)
    assert capsys.readouterr().out == 'sudo kill `cat pid`\nsudo rm -f pid\ncalled remove_result()\n'


def test_restart(monkeypatch, capsys):
    """unittest for tasks_hgweb.restart
    """
    def mock_start(*args):
        """stub
        """
        print('called start()')
    def mock_stop(*args):
        """stub
        """
        print('called stop()')
    monkeypatch.setattr(tasks_hgweb, 'start', mock_start)
    monkeypatch.setattr(tasks_hgweb, 'stop', mock_stop)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_hgweb.restart(c)
    assert capsys.readouterr().out == ('called stop()\ncalled start()\n')
