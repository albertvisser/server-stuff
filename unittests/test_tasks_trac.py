"""unittests for ./testee.py
"""
from invoke import MockContext
import tasks_trac as testee


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
        print('called report_result')
    monkeypatch.setattr(testee, 'trac_pid', 'pid')
    monkeypatch.setattr(testee, 'trac_sock', 'socket')
    monkeypatch.setattr(testee, 'check_result', mock_check)
    monkeypatch.setattr(testee, 'report_result', mock_report)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.start(c)
    assert capsys.readouterr().out == 'called check_result\ntrac xxx\n'
    monkeypatch.setattr(testee, 'check_result', mock_check_2)
    testee.start(c)
    # assert capsys.readouterr().out == ('sudo /usr/bin/gunicorn -D -b unix:socket -p pid '
    #                                    'tracwsgi:application\ncalled report_result\n')
    assert capsys.readouterr().out == (
            'called check_result\n'
            # 'sudo tracd -d --pidfile=pid -p 9000'
            'sudo /home/albert/.tracvenv/bin/tracd -d --pidfile=pid -p 9000'
            ' --basic-auth="*,/home/albert/lemontrac/trac_users, lemontrac"'
            ' --protocol=http -s /home/albert/lemontrac\n'
            'called report_result\n')


def test_stop(monkeypatch, capsys):
    """unittest for testee.stop
    """
    def mock_remove(*args):
        """stub
        """
        print('called remove_result')
    monkeypatch.setattr(testee, 'trac_pid', 'pid')
    monkeypatch.setattr(testee, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.stop(c)
    assert capsys.readouterr().out == 'sudo kill `cat pid`\nsudo rm -f pid\ncalled remove_result\n'


def test_restart(monkeypatch, capsys):
    """unittest for testee.restart
    """
    def mock_start(*args):
        """stub
        """
        print('called trac_start')
    def mock_stop(*args):
        """stub
        """
        print('called trac_stop')
    monkeypatch.setattr(testee, 'start', mock_start)
    monkeypatch.setattr(testee, 'stop', mock_stop)
    c = MockContext()
    testee.restart(c)
    assert capsys.readouterr().out == 'called trac_stop\ncalled trac_start\n'


def test_editconf(monkeypatch, capsys):
    """unittest for testee.editconf
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.editconf(c)
    assert capsys.readouterr().out == 'fabsrv editconf trac\n'


def test_modconf(monkeypatch, capsys):
    """unittest for testee.modconf
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.modconf(c)
    assert capsys.readouterr().out == 'fabsrv modconf -n trac\n'
