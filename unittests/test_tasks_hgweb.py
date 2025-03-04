"""unittests for ./testee.py
"""
from invoke import MockContext
import tasks_hgweb as testee


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


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
        print('called report_result()')
    testee.HGWEB = 'here'
    testee.hgweb_pid = 'pid'
    testee.hgweb_sock = 'socket'
    monkeypatch.setattr(testee, 'report_result', mock_report)
    monkeypatch.setattr(testee, 'check_result', mock_check)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.start(c)
    assert capsys.readouterr().out == 'called check_result\nhgweb xxx\n'
    monkeypatch.setattr(testee, 'check_result', mock_check_2)
    testee.start(c)
    assert capsys.readouterr().out == (
            'called check_result\n'
            # 'sudo spawn-fcgi -f here/hgweb.fcgi -s socket -P pid -u www-data\n'
            'sudo /usr/bin/gunicorn -b unix:socket -p pid hgwebwsgi:application\n'
            'called report_result()\n')


def test_stop(monkeypatch, capsys):
    """unittest for testee.stop
    """
    def mock_remove(*args):
        """stub
        """
        print('called remove_result()')
    testee.hgweb_pid = 'pid'
    monkeypatch.setattr(testee, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.stop(c)
    assert capsys.readouterr().out == 'sudo kill `cat pid`\nsudo rm -f pid\ncalled remove_result()\n'


def test_restart(monkeypatch, capsys):
    """unittest for testee.restart
    """
    def mock_start(*args):
        """stub
        """
        print('called start()')
    def mock_stop(*args):
        """stub
        """
        print('called stop()')
    monkeypatch.setattr(testee, 'start', mock_start)
    monkeypatch.setattr(testee, 'stop', mock_stop)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.restart(c)
    assert capsys.readouterr().out == ('called stop()\ncalled start()\n')
