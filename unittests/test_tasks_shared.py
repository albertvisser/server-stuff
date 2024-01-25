"""unittests for ./tasks_shared.py
"""
import types
import pathlib
from invoke import MockContext
import tasks_shared


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def test_add_conf(monkeypatch, capsys):
    """unittest for tasks_shared.add_conf
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_shared.add_conf(c, 'config', 'avail_loc', 'enabl_loc')
    assert capsys.readouterr().out == 'sudo ln -s avail_loc/config enabl_loc/config\n'


def test_remove_conf(monkeypatch, capsys):
    """unittest for tasks_shared.remove_conf
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_shared.remove_conf(c, 'config', 'enabl_loc')
    assert capsys.readouterr().out == 'sudo rm enabl_loc/config\n'


def test_mod_conf(monkeypatch, capsys):
    """unittest for tasks_shared.mod_conf
    """
    class MockDatetime:
        """stub
        """
        @classmethod
        def today(cls):
            """stub
            """
            return MockDatetime()
        @classmethod
        def strftime(cls, datestring):
            """stub
            """
            return 'today'
    def mock_run(self, *args):
        """stub
        """
        print(f'execute in {self.cwd}')
        print(*args)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_shared.mod_conf(c, 'from/file', 'to')
    assert capsys.readouterr().out == 'execute in from\nsudo cp file to\n'
    tasks_shared.mod_conf(c, 'from/file', 'to', needs_sudo=False)
    assert capsys.readouterr().out == 'execute in from\n cp file to\n'
    monkeypatch.setattr(tasks_shared.datetime, 'datetime', MockDatetime)
    tasks_shared.mod_conf(c, 'from/file', 'to', backup=True)
    assert capsys.readouterr().out == ('execute in from\nmkdir -m 777 backup\n'
                                       'execute in from\ncp to/file backup/file-today\n'
                                       'execute in from\nsudo cp file to\n')
    tasks_shared.mod_conf(c, 'from/file', 'to', append=True)
    assert capsys.readouterr().out == ('execute in from\nmkdir -m 777 backup\n'
                                       'execute in from\ncp to/file backup/file-today\n'
                                       'execute in from\ncp file file~~\n'
                                       'execute in from\ncat backup/file-today file > file~~~\n'
                                       'execute in from\nmv -f file~~~ file\n'
                                       'execute in from\nsudo cp file to\n'
                                       'execute in from\nmv -f file~~ file\n')


def test_compare(capsys):
    """unittest for tasks_shared.compare
    """
    tasks_shared.do_compare('local', 'remote')
    assert capsys.readouterr().out == 'comparing local with remote\n'


def test_report_result():
    """unittest for tasks_shared.report_result
    """
    # eigenlijk moet ik het resultaat van umask ook nog checken
    result = types.SimpleNamespace(stdout='stdout', stderr='stderr')
    tasks_shared.report_result('testproj', result)
    path1 = pathlib.Path('/tmp/server-testproj-ok')
    assert path1.read_text() == 'stdout\n'
    path2 = pathlib.Path('/tmp/server-testproj-err')
    assert path2.read_text() == 'stderr\n'
    # teardown
    path1.unlink()
    path2.unlink()


def test_remove_result(monkeypatch, capsys):
    """unittest for tasks_shared.remove_result
    """
    path1 = pathlib.Path('/tmp/server-testproj-ok')
    path2 = pathlib.Path('/tmp/server-testproj-err')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_shared.remove_result(c, 'testproj')
    assert capsys.readouterr().out == f'sudo rm -f {path1}\nsudo rm -f {path2}\n'
