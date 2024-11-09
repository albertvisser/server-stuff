"""unittests for ./testee.py
"""
from invoke import MockContext
import tasks_plone as testee


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args, 'in', self.cwd)


def mock_plone(*args):
    """stub stub for testee._plone
    """
    print('called _plone with args', *args)


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
    monkeypatch.setattr(testee, '_plone', mock_plone)
    monkeypatch.setattr(testee, 'check_result', mock_check)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.start(c, 'plone')
    assert capsys.readouterr().out == 'called check_result\nplone xxx\n'
    monkeypatch.setattr(testee, 'check_result', mock_check_2)
    testee.start(c, 'plone')
    assert capsys.readouterr().out == (
            "called check_result\n"
            "sudo docker run --name plone6-backend -e SITE=Plone -e CORS_ALLOW_ORIGIN='*'"
            " -d -p 8085:8085 plone/plone-backend:6.0 in \n"
            "sudo docker run --name plone6-frontend --link plone6-backend:backend"
            " -e RAZZLE_API_PATH=http://localhost:8085/Plone"
            " -e RAZZLE_INTERNAL_API_PATH=http://backend:8085/Plone"
            " -d -p 8090:8090 plone/plone-frontend:latest in \n")


def test_stop(monkeypatch, capsys):
    """unittest for testee.stop
    """
    monkeypatch.setattr(testee, '_plone', mock_plone)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.stop(c, 'plone')
    assert capsys.readouterr().out == (
            'sudo docker stop plone6-frontend && sudo docker rm plone6-frontend in \n'
            'sudo docker stop plone6-backend && sudo docker rm plone6-backend in \n')


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
    testee.restart(c, 'plone')
    assert capsys.readouterr().out == ('called stop()\ncalled start()\n')


def test_buildout(monkeypatch, capsys):
    """unittest for testee.buildout
    """
    monkeypatch.setattr(testee, '_plone', mock_plone)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee.buildout(c, 'plone')
    assert capsys.readouterr().out == 'called _plone with args MockContext buildout plone\n'


def test_plone(monkeypatch, capsys):
    """unittest for testee.plone
    """
    def mock_report(*args):
        """stub
        """
        print('called report_result()')
    def mock_remove(*args):
        """stub
        """
        print('called remove_result()')
    testee.HOME = 'home'
    testee.PLONES = ['site', 'name']
    monkeypatch.setattr(testee, 'report_result', mock_report)
    monkeypatch.setattr(testee, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    testee._plone(c, 'start', '')
    assert capsys.readouterr().out == ('bin/plonectl start in home/Site/zinstance\n'
                                       'called report_result()\n'
                                       'bin/plonectl start in home/Name/zinstance\n'
                                       'called report_result()\n')
    testee._plone(c, 'stop', 'site')
    assert capsys.readouterr().out == ('bin/plonectl stop in home/Site/zinstance\n'
                                       'called remove_result()\n')
    testee._plone(c, 'buildout', 'one,two')
    assert capsys.readouterr().out == ('bin/buildout in home/One/zinstance\n'
                                       'bin/buildout in home/Two/zinstance\n')
    testee._plone(c, 'other', 'site')
    assert capsys.readouterr().out == "unknown action\n"
