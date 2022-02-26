import pytest
from invoke import MockContext
import tasks_plone


def mock_run(self, *args):
    print(*args, 'in', self.cwd)


def mock_plone(*args):
    print('called _plone with args', *args)


def test_start(monkeypatch, capsys):
    monkeypatch.setattr(tasks_plone, '_plone', mock_plone)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks_plone.start(c, 'plone')
    assert capsys.readouterr().out == 'called _plone with args MockContext start plone\n'


def test_stop(monkeypatch, capsys):
    monkeypatch.setattr(tasks_plone, '_plone', mock_plone)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks_plone.stop(c, 'plone')
    assert capsys.readouterr().out == 'called _plone with args MockContext stop plone\n'


def test_restart(monkeypatch, capsys):
    def mock_start(*args):
        print('called start()')
    def mock_stop(*args):
        print('called stop()')
    monkeypatch.setattr(tasks_plone, 'start', mock_start)
    monkeypatch.setattr(tasks_plone, 'stop', mock_stop)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_plone.restart(c, 'plone')
    assert capsys.readouterr().out == ('called stop()\ncalled start()\n')


def test_buildout(monkeypatch, capsys):
    monkeypatch.setattr(tasks_plone, '_plone', mock_plone)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks_plone.buildout(c, 'plone')
    assert capsys.readouterr().out == 'called _plone with args MockContext buildout plone\n'


def test_plone(monkeypatch, capsys):
    def mock_report(*args):
        print('called report_result()')
    def mock_remove(*args):
        print('called remove_result()')
    tasks_plone.HOME = 'home'
    tasks_plone.PLONES = ['site', 'name']
    monkeypatch.setattr(tasks_plone, 'report_result', mock_report)
    monkeypatch.setattr(tasks_plone, 'remove_result', mock_remove)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'MockContext')
    c = MockContext()
    tasks_plone._plone(c, 'start', '')
    assert capsys.readouterr().out == ('bin/plonectl start in home/Site/zinstance\n'
                                       'called report_result()\n'
                                       'bin/plonectl start in home/Name/zinstance\n'
                                       'called report_result()\n')
    tasks_plone._plone(c, 'stop', 'site')
    assert capsys.readouterr().out == ('bin/plonectl stop in home/Site/zinstance\n'
                                       'called remove_result()\n')
    tasks_plone._plone(c, 'buildout', 'one,two')
    assert capsys.readouterr().out == ('bin/buildout in home/One/zinstance\n'
                                       'bin/buildout in home/Two/zinstance\n')
