"""unittests for ./tasks_nginx.py
"""
from invoke import MockContext
import tasks_nginx


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
    tasks_nginx.extconf = {'test': ('to', True, '@file')}
    tasks_nginx.AVAIL = 'avail'
    tasks_nginx.FROM = 'from'
    tasks_nginx._diffconf(c, 'test')
    assert capsys.readouterr().out == 'diff -s to/testfile from/testfile\n'
    tasks_nginx._diffconf(c, 'other', gui=True)
    assert capsys.readouterr().out == 'meld avail/other from/other\n'


def test_addconf(monkeypatch, capsys):
    """unittest for tasks_nginx.addconf
    """
    monkeypatch.setattr(tasks_nginx.shared, 'add_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_nginx.AVAIL = 'avail'
    tasks_nginx.ENABL = 'enabl'
    tasks_nginx.addconf(c)
    assert capsys.readouterr().out == ''
    tasks_nginx.addconf(c, 'this ,that')
    assert capsys.readouterr().out == ('call shared function with args Mock this avail enabl {}\n'
                                       'call shared function with args Mock that avail enabl {}\n')


def test_rmconf(monkeypatch, capsys):
    """unittest for tasks_nginx.rmconf
    """
    monkeypatch.setattr(tasks_nginx.shared, 'remove_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_nginx.ENABL = 'enabl'
    tasks_nginx.rmconf(c, 'this ,that')
    assert capsys.readouterr().out == ('call shared function with args Mock this enabl {}\n'
                                       'call shared function with args Mock that enabl {}\n')


def test_modconf(monkeypatch, capsys):
    """unittest for tasks_nginx.modconf
    """
    monkeypatch.setattr(tasks_nginx.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_nginx.FROM = 'from'
    tasks_nginx.modconf(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail {}\n'
                                       'call shared function with args Mock from/that avail {}\n')


def test_modconfb(monkeypatch, capsys):
    """unittest for tasks_nginx.modconfb
    """
    monkeypatch.setattr(tasks_nginx.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_nginx.FROM = 'from'
    tasks_nginx.modconfb(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail'
                                       " {'backup': True}\n"
                                       'call shared function with args Mock from/that avail'
                                       " {'backup': True}\n")


def test_modconfa(monkeypatch, capsys):
    """unittest for tasks_nginx.modconfa
    """
    monkeypatch.setattr(tasks_nginx.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_nginx.FROM = 'from'
    tasks_nginx.modconfa(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail'
                                       " {'append': True}\n"
                                       'call shared function with args Mock from/that avail'
                                       " {'append': True}\n")


def test_newconf(monkeypatch, capsys):
    """unittest for tasks_nginx.newconf
    """
    monkeypatch.setattr(tasks_nginx.shared, 'add_conf', mock_call)
    monkeypatch.setattr(tasks_nginx.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_nginx.AVAIL = 'avail'
    tasks_nginx.ENABL = 'enabl'
    tasks_nginx.FROM = 'from'
    tasks_nginx.newconf(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail {}\n'
                                       'call shared function with args Mock this avail enabl {}\n'
                                       'call shared function with args Mock from/that avail {}\n'
                                       'call shared function with args Mock that avail enabl {}\n')


def test_diffconf(monkeypatch, capsys):
    """unittest for tasks_nginx.diffconf
    """
    monkeypatch.setattr(tasks_nginx, '_diffconf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_nginx.diffconf(c, 'this, that')
    assert capsys.readouterr().out == ('call shared function with args Mock this {}\n'
                                       'call shared function with args Mock that {}\n')


def test_diffconfg(monkeypatch, capsys):
    """unittest for tasks_nginx.diffconfg
    """
    monkeypatch.setattr(tasks_nginx, '_diffconf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_nginx.diffconfg(c, 'this, that')
    assert capsys.readouterr().out == ("call shared function with args Mock this {'gui': True}\n"
                                       "call shared function with args Mock that {'gui': True}\n")


def test_list(capsys):
    """unittest for tasks_nginx.list
    """
    tasks_nginx.intconf = {'int2': (), 'int1': ()}
    tasks_nginx.extconf = {'ext2': (), 'ext1': ()}
    c = MockContext()
    tasks_nginx.list(c)
    assert capsys.readouterr().out == ("Available Nginx configs: int1, int2\n"
                                       "Available non-Nginx confs: ext1, ext2\n")


def test_editconf(monkeypatch, capsys):
    """unittest for tasks_nginx.editconf
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_nginx.EDITORCMD = 'xedit {}'
    tasks_nginx.FROM = 'from'
    tasks_nginx.editconf(c, 'name')
    assert capsys.readouterr().out == 'xedit from/name\n'


def test_list_domains(monkeypatch, capsys):
    """unittest for tasks_nginx.list_domains
    """
    tasks_nginx.intconf = {'int2': ('domain2',), 'int1': ('domain1', 'domain')}
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_nginx.list_domains(c)
    assert capsys.readouterr().out == ('domains for config "int2": domain2\n'
                                       'domains for config "int1": domain1, domain\n')
    tasks_nginx.list_domains(c, 'int2')
    assert capsys.readouterr().out == ('domains for config "int2": domain2\n')
    tasks_nginx.list_domains(c, 'this,that')
    assert capsys.readouterr().out == ('unknown config "this"\nunknown config "that"\n')


def test_start(monkeypatch, capsys):
    """unittest for tasks_nginx.start
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_nginx.start(c)
    assert capsys.readouterr().out == 'sudo systemctl start nginx.service\n'


def test_stop(monkeypatch, capsys):
    """unittest for tasks_nginx.stop
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_nginx.stop(c)
    assert capsys.readouterr().out == 'sudo systemctl stop nginx.service\n'


def test_restart(monkeypatch, capsys):
    """unittest for tasks_nginx.restart
    """
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_nginx.restart(c)
    assert capsys.readouterr().out == 'sudo systemctl restart nginx.service\n'


def test_compare(monkeypatch, capsys):
    """unittest for tasks_nginx.compare
    """
    tasks_nginx.AVAIL = 'avail'
    tasks_nginx.FROM = 'from'
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_nginx.compare(c)
    assert capsys.readouterr().out == 'diff -s from avail\n'


def test_compareg(monkeypatch, capsys):
    """unittest for tasks_nginx.compareg
    """
    tasks_nginx.AVAIL = 'avail'
    tasks_nginx.FROM = 'from'
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_nginx.compareg(c)
    assert capsys.readouterr().out == 'meld from avail\n'
