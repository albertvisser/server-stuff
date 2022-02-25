import pytest
from invoke import MockContext
import tasks_apache


def mock_run(self, *args):
    print(*args)


def mock_call(*args, **kwargs):
    print('call shared function with args', *args, kwargs)


def test_start(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_apache.start(c)
    assert capsys.readouterr().out == 'sudo /etc/init.d/apache2 start\n'
    # assert capsys.readouterr().out == 'sudo systemctl start apache.service\n'


def test_stop(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_apache.stop(c)
    assert capsys.readouterr().out == 'sudo /etc/init.d/apache2 stop\n'
    # assert capsys.readouterr().out == 'sudo systemctl stop apache.service\n'


def test_restart(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_apache.restart(c)
    assert capsys.readouterr().out == 'sudo /etc/init.d/apache2 restart\n'
    # assert capsys.readouterr().out == 'sudo systemctl restart apache.service\n'


# def test_diffconf_subroutine(monkeypatch, capsys):
#     monkeypatch.setattr(MockContext, 'run', mock_run)
#     c = MockContext()
#     tasks_apache.extconf = {'test': ('to', True, '@file')}
#     tasks_apache.AVAIL = 'avail'
#     tasks_apache.FROM = 'from'
#     tasks_apache._diffconf(c, 'test')
#     assert capsys.readouterr().out == 'diff -s to/testfile from/testfile\n'
#     tasks_apache._diffconf(c, 'other', gui=True)
#     assert capsys.readouterr().out == 'meld avail/other from/other\n'


def test_addconf(monkeypatch, capsys):
    monkeypatch.setattr(tasks_apache.shared, 'add_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_apache.A_AVAIL = 'avail'
    tasks_apache.A_ENABL = 'enabl'
    tasks_apache.addconf(c)
    assert capsys.readouterr().out == ''
    tasks_apache.addconf(c, 'this ,that')
    assert capsys.readouterr().out == ('call shared function with args Mock this  avail enabl {}\n'
                                       'call shared function with args Mock that avail enabl {}\n')


def test_editconf(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_apache.EDITORCMD = 'xedit {}'
    tasks_apache.FROM = 'from'
    tasks_apache.editconf(c, 'name')
    assert capsys.readouterr().out == 'xedit from/name\n'


def test_modconf(monkeypatch, capsys):
    monkeypatch.setattr(tasks_apache.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_apache.FROM = 'from'
    tasks_apache.A_AVAIL = 'avail'
    tasks_apache.modconf(c)
    assert capsys.readouterr().out == ''
    tasks_apache.modconf(c, 'this,that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail {}\n'
                                       'call shared function with args Mock from/that avail {}\n')


def test_modconfb(monkeypatch, capsys):
    monkeypatch.setattr(tasks_apache.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_apache.FROM = 'from'
    tasks_apache.A_AVAIL = 'avail'
    tasks_apache.modconfb(c)
    assert capsys.readouterr().out == ''
    tasks_apache.modconfb(c, 'this,that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail'
                                       " {'backup': True}\n"
                                       'call shared function with args Mock from/that avail'
                                       " {'backup': True}\n")


def test_modconfa(monkeypatch, capsys):
    monkeypatch.setattr(tasks_apache.shared, 'mod_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_apache.FROM = 'from'
    tasks_apache.A_AVAIL = 'avail'
    tasks_apache.modconfa(c)
    assert capsys.readouterr().out == ''
    tasks_apache.modconfa(c, 'this,that')
    assert capsys.readouterr().out == ('call shared function with args Mock from/this avail'
                                       " {'append': True}\n"
                                       'call shared function with args Mock from/that avail'
                                       " {'append': True}\n")


def test_rmconf(monkeypatch, capsys):
    monkeypatch.setattr(tasks_apache.shared, 'remove_conf', mock_call)
    monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
    c = MockContext()
    tasks_apache.A_AVAIL = 'avail'
    tasks_apache.A_ENABL = 'enabl'
    tasks_apache.rmconf(c)
    assert capsys.readouterr().out == ''
    tasks_apache.rmconf(c, 'this,that')
    assert capsys.readouterr().out == ('call shared function with args Mock this enabl {}\n'
                                       'call shared function with args Mock that enabl {}\n')


# def test_newconf(monkeypatch, capsys):
#     monkeypatch.setattr(tasks_apache.shared, 'add_conf', mock_call)
#     monkeypatch.setattr(tasks_apache.shared, 'mod_conf', mock_call)
#     monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
#     c = MockContext()
#     tasks_apache.AVAIL = 'avail'
#     tasks_apache.ENABL = 'enabl'
#     tasks_apache.FROM = 'from'
#     tasks_apache.newconf(c, 'this, that')
#     assert capsys.readouterr().out == ('call shared function with args Mock from/this avail {}\n'
#                                        'call shared function with args Mock this avail enabl {}\n'
#                                        'call shared function with args Mock from/that avail {}\n'
#                                        'call shared function with args Mock that avail enabl {}\n')


# def test_diffconf(monkeypatch, capsys):
#     monkeypatch.setattr(tasks_apache, '_diffconf', mock_call)
#     monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
#     c = MockContext()
#     tasks_apache.diffconf(c, 'this, that')
#     assert capsys.readouterr().out == ('call shared function with args Mock this {}\n'
#                                        'call shared function with args Mock that {}\n')


# def test_diffconfg(monkeypatch, capsys):
#     monkeypatch.setattr(tasks_apache, '_diffconf', mock_call)
#     monkeypatch.setattr(MockContext, '__str__', lambda x: 'Mock')
#     c = MockContext()
#     tasks_apache.diffconfg(c, 'this, that')
#     assert capsys.readouterr().out == ("call shared function with args Mock this {'gui': True}\n"
#                                        "call shared function with args Mock that {'gui': True}\n")


# def test_list(monkeypatch, capsys):
#     tasks_apache.intconf = {'int2': (), 'int1': ()}
#     tasks_apache.extconf = {'ext2': (), 'ext1': ()}
#     c = MockContext()
#     tasks_apache.list(c)
#     assert capsys.readouterr().out == ("Available Nginx configs: int1, int2\n"
#                                        "Available non-Nginx confs: ext1, ext2\n")


# def test_list_domains(monkeypatch, capsys):
#     tasks_apache.intconf = {'int2': ('domain2',), 'int1': ('domain1', 'domain')}
#     monkeypatch.setattr(MockContext, 'run', mock_run)
#     c = MockContext()
#     tasks_apache.list_domains(c)
#     assert capsys.readouterr().out == ('domains for config "int2": domain2\n'
#                                        'domains for config "int1": domain1, domain\n')
#     tasks_apache.list_domains(c, 'int2')
#     assert capsys.readouterr().out == ('domains for config "int2": domain2\n')
#     tasks_apache.list_domains(c, 'this,that')
#     assert capsys.readouterr().out == ('unknown config "this"\nunknown config "that"\n')


def test_compare(monkeypatch, capsys):
    tasks_apache.A_AVAIL = 'avail'
    tasks_apache.FROM = 'from'
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_apache.compare(c)
    assert capsys.readouterr().out == 'diff -s from avail\n'


def test_compareg(monkeypatch, capsys):
    tasks_apache.A_AVAIL = 'avail'
    tasks_apache.FROM = 'from'
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    tasks_apache.compareg(c)
    assert capsys.readouterr().out == 'meld from avail\n'
