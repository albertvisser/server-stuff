from invoke import MockContext
import tasks_php


def mock_run(self, *args):
    print(*args)


def test_php_start(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_php.start(c)
    assert capsys.readouterr().out == 'sudo systemctl start php-fpm.service\n'


def test_php_stop(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_php.stop(c)
    assert capsys.readouterr().out == 'sudo systemctl stop php-fpm.service\n'


def test_php_restart(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_php.restart(c)
    assert capsys.readouterr().out == 'sudo systemctl restart php-fpm.service\n'
