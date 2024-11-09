"""unittests for ./tasks_nginx.py
"""
from invoke import MockContext
import tasks_nginx as testee


def mock_run(self, *args):
    """stub for invoke.Context.run
    """
    print(*args)


def mock_call(*args, **kwargs):
    """generic stub for helper functions imported from shared.py
    """
    print('call shared function with args', *args, kwargs)


def test_diffconf_subroutine(monkeypatch, capsys):
    """unittest for tasks_nginx.diffconf_subroutine
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.extconf = {'test': ('to', True, '@file')}
    testee.AVAIL = 'avail'
    testee.FROM = 'from'
    testee._diffconf(c, 'test')
    assert capsys.readouterr().out == 'diff -s to/testfile from/testfile\n'
    testee.extconf = {'test': ('to', True, 'file')}
    testee._diffconf(c, 'test')
    assert capsys.readouterr().out == 'diff -s to/file from/file\n'
    testee._diffconf(c, 'other', gui=True)
    assert capsys.readouterr().out == 'meld avail/other from/other\n'


def test_addconf(monkeypatch, capsys):
    """unittest for tasks_nginx.addconf
    """
    monkeypatch.setattr(testee.shared, 'add_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    testee.AVAIL = 'avail'
    testee.ENABL = 'enabl'
    testee.addconf(c, 'this ,that')
    assert capsys.readouterr().out == ('call shared function with args Mock this avail enabl {}\n'
                                       'call shared function with args Mock that avail enabl {}\n')


def test_rmconf(monkeypatch, capsys):
    """unittest for tasks_nginx.rmconf
    """
    monkeypatch.setattr(testee.shared, 'remove_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    testee.ENABL = 'enabl'
    testee.rmconf(c, 'this ,that')
    assert capsys.readouterr().out == ('call shared function with args Mock this enabl {}\n'
                                       'call shared function with args Mock that enabl {}\n')


def test_modconf(monkeypatch, capsys):
    """unittest for tasks_nginx.modconf
    """
    monkeypatch.setattr(testee.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    testee.FROM = 'from'
    testee.modconf(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail {}\n'
                                       'call shared function with args Mock from/that avail {}\n')


def test_modconfb(monkeypatch, capsys):
    """unittest for tasks_nginx.modconfb
    """
    monkeypatch.setattr(testee.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    testee.FROM = 'from'
    testee.modconfb(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail'
                                       " {'backup': True}\n"
                                       'call shared function with args Mock from/that avail'
                                       " {'backup': True}\n")


def test_modconfa(monkeypatch, capsys):
    """unittest for tasks_nginx.modconfa
    """
    monkeypatch.setattr(testee.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    testee.FROM = 'from'
    testee.modconfa(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail'
                                       " {'append': True}\n"
                                       'call shared function with args Mock from/that avail'
                                       " {'append': True}\n")


def test_newconf(monkeypatch, capsys):
    """unittest for tasks_nginx.newconf
    """
    monkeypatch.setattr(testee.shared, 'add_conf', mock_call)
    monkeypatch.setattr(testee.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    testee.AVAIL = 'avail'
    testee.ENABL = 'enabl'
    testee.FROM = 'from'
    testee.newconf(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail {}\n'
                                       'call shared function with args Mock this avail enabl {}\n'
                                       'call shared function with args Mock from/that avail {}\n'
                                       'call shared function with args Mock that avail enabl {}\n')


def test_diffconf(monkeypatch, capsys):
    """unittest for tasks_nginx.diffconf
    """
    testee.AVAIL = 'avail'
    testee.FROM = 'from'
    monkeypatch.setattr(testee, '_diffconf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.diffconf(c)
    assert capsys.readouterr().out == 'diff -s from avail\n'
    testee.diffconf(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock this {}\n'
                                       'call shared function with args Mock that {}\n')


def test_diffconfg(monkeypatch, capsys):
    """unittest for tasks_nginx.diffconfg
    """
    testee.AVAIL = 'avail'
    testee.FROM = 'from'
    monkeypatch.setattr(testee, '_diffconf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.diffconfg(c)
    assert capsys.readouterr().out == 'meld from avail\n'
    testee.diffconfg(c, 'this, that')
    assert capsys.readouterr().out == ("call shared function with args Mock this {'gui': True}\n"
                                       "call shared function with args Mock that {'gui': True}\n")


def test_list(capsys):
    """unittest for tasks_nginx.list
    """
    testee.intconf = {'int2': (), 'int1': ()}
    testee.extconf = {'ext2': (), 'ext1': ()}
    c = MockContext()
    testee.list(c)
    assert capsys.readouterr().out == ("Available Nginx configs: int1, int2\n"
                                       "Available non-Nginx confs: ext1, ext2\n")


def test_editconf(monkeypatch, capsys):
    """unittest for tasks_nginx.editconf
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.EDITORCMD = 'xedit {}'
    testee.FROM = 'from'
    testee.editconf(c, 'name')
    assert capsys.readouterr().out == 'xedit from/name\n'


def test_list_domains(monkeypatch, capsys):
    """unittest for tasks_nginx.list_domains
    """
    testee.intconf = {'int2': ('domain2',), 'int1': ('domain1', 'domain')}
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.list_domains(c)
    assert capsys.readouterr().out == ('domains for config "int2": domain2\n'
                                       'domains for config "int1": domain1, domain\n')
    testee.list_domains(c, 'int2')
    assert capsys.readouterr().out == ('domains for config "int2": domain2\n')
    testee.list_domains(c, 'this,that')
    assert capsys.readouterr().out == ('unknown config "this"\nunknown config "that"\n')


def test_start(monkeypatch, capsys):
    """unittest for tasks_nginx.start
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.start(c)
    assert capsys.readouterr().out == 'sudo systemctl start nginx.service\n'


def test_stop(monkeypatch, capsys):
    """unittest for tasks_nginx.stop
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.stop(c)
    assert capsys.readouterr().out == 'sudo systemctl stop nginx.service\n'


def test_restart(monkeypatch, capsys):
    """unittest for tasks_nginx.restart
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    testee.restart(c)
    assert capsys.readouterr().out == 'sudo systemctl restart nginx.service\n'
