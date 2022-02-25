import pytest
from invoke import MockContext
import tasks_ftp


def mock_run(self, *args):
    print(*args)


def test_ftp_start(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_ftp.start(c)
    assert capsys.readouterr().out == 'sudo start vsftpd\n'


def test_ftp_stop(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_ftp.stop(c)
    assert capsys.readouterr().out == 'sudo stop vsftpd\n'


def test_ftp_restart(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_ftp.restart(c)
    assert capsys.readouterr().out == 'sudo restart vsftpd\n'
