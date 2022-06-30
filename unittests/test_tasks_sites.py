import os
import pytest
import types
from invoke import MockContext
import tasks_sites


def mock_run(self, *args):
    print(*args)


def print_args(*args, **kwargs):
    print('called routine with args', *args, kwargs)


def test_list_domains(monkeypatch, capsys):
    monkeypatch.setattr(tasks_sites, 'get_sitenames', lambda: ('name', 'another_name'))
    tasks_sites.list_domains(MockContext())
    assert capsys.readouterr().out == 'defined domains:\nname\nanother_name\n'


def test_check_up(monkeypatch, capsys):
    monkeypatch.setattr(tasks_sites, 'check_sites', print_args)
    tasks_sites.check_up(MockContext())
    assert capsys.readouterr().out == "called routine with args {'up_only': True}\n"


def test_check_all(monkeypatch, capsys):
    monkeypatch.setattr(tasks_sites, 'check_sites', print_args)
    tasks_sites.check_all(MockContext())
    assert capsys.readouterr().out == "called routine with args {}\n"


def test_check_pages(monkeypatch, capsys):
    monkeypatch.setattr(tasks_sites, 'check_sites', print_args)
    tasks_sites.check_pages(MockContext(), 'this,that')
    assert capsys.readouterr().out == ("called routine with args "
                                       "{'quick': False, 'sites': ['this', 'that']}\n")


def test_check_all_pages(monkeypatch, capsys):
    monkeypatch.setattr(tasks_sites, 'check_sites', print_args)
    tasks_sites.check_all_pages(MockContext())
    assert capsys.readouterr().out == ("called routine with args {'quick': False}\n")


def test_check_project(monkeypatch, capsys):
    monkeypatch.setattr(tasks_sites, 'check_sites', print_args)
    tasks_sites.check_project(MockContext(), 'this,magiokis,magiokis-test,rst2html')
    assert capsys.readouterr().out == ("called routine with args {'quick': False, "
                                       "'sites': ['this.lemoncurry.nl', 'original.magiokis.nl', "
                                       "'songs.magiokis.nl', 'vertel.magiokis.nl', "
                                       "'denk.magiokis.nl', 'dicht.magiokis.nl', 'test.magiokis.nl', "
                                       "'rst2html.lemoncurry.nl', 'rst2html-mongo.lemoncurry.nl', "
                                       "'rst2html-pg.lemoncurry.nl']}\n")


def test_check_sites(monkeypatch, capsys):
    monkeypatch.setattr(tasks_sites, 'get_sitenames', lambda: ('name', 'another_name'))
    monkeypatch.setattr(tasks_sites, 'check_frontpage', lambda x: 201)
    tasks_sites.check_sites()
    assert capsys.readouterr().out == ('checking name... error 201\n'
                                       'checking another_name... error 201\n')
    monkeypatch.setattr(tasks_sites, 'get_sitenames', lambda: ('name', 'another_name'))
    tasks_sites.check_sites(sites=['name', 'not_a_name'])
    assert capsys.readouterr().out == ('checking name... error 201\n')
    monkeypatch.setattr(tasks_sites, 'check_frontpage', lambda x: 200)
    tasks_sites.check_sites(sites=['name'], up_only=True)
    assert capsys.readouterr().out == ('checking name... ok\n')
    tasks_sites.check_address = {'quick': {}}
    tasks_sites.check_sites(sites=['name'])
    assert capsys.readouterr().out == ('checking name... ok\n')
    tasks_sites.check_address = {'quick': {'name': 'page'}}
    monkeypatch.setattr(tasks_sites, 'check_page', lambda x: types.SimpleNamespace(status_code=201))
    tasks_sites.check_sites(sites=['name'], quick=True)
    assert capsys.readouterr().out == ('checking name... ok\n    error 201 on namepage\n')
    tasks_sites.check_address = {'full': {}}
    tasks_sites.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok\n'
                                       '    check_address entry missing for name\n')
    tasks_sites.check_address = {'full': {'name': ''}}
    tasks_sites.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok, no further checking necessary\n')
    tasks_sites.check_address = {'full': {'name': 'name-urls'}}
    urlfiles_dir = os.path.expanduser(os.path.join('~', 'nginx-config', 'check-pages'))
    if os.path.exists(urlfiles_dir):
        os.remove(os.path.join(urlfiles_dir, 'name-urls'))
    tasks_sites.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok\n'
                                       '    check-pages file missing for name\n')
    try:
        os.mkdir(urlfiles_dir)
    except FileExistsError:
        pass
    with open(os.path.join(urlfiles_dir, 'name-urls'), 'w') as out:
        out.write('/testurl')
    tasks_sites.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok\n'
                                       '    checking name/testurl... error 201\n')
    monkeypatch.setattr(tasks_sites, 'check_page', lambda x: types.SimpleNamespace(status_code=200))
    tasks_sites.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok\n'
                                       '    checking name/testurl... ok\n')


def test_check_page(monkeypatch, capsys):
    def mock_get(*args):
        return args[0]
    monkeypatch.setattr(tasks_sites.requests, 'get', mock_get)
    assert tasks_sites.check_page('somesite') == 'http://somesite'


def test_check_frontpage(monkeypatch, capsys):
    def mock_check(*args):
        return types.SimpleNamespace(status_code=200)
    def mock_check_2(*args):
        return types.SimpleNamespace(status_code=401)
    monkeypatch.setattr(tasks_sites, 'check_page', mock_check)
    assert tasks_sites.check_frontpage('somesite') == 200
    monkeypatch.setattr(tasks_sites, 'check_page', mock_check_2)
    assert tasks_sites.check_frontpage('tracsite') == 200


def test_get_sitenames(monkeypatch, capsys):
    filedata = ('xxx  lennoncurry\nxxx  lemoncurry.nl\nxx test.magiokis.nl\n'
                '# deze regel niet laten zien\nxxx  jansen')
    testfile = '/tmp/hoststest'
    with open(testfile, 'w') as out:
        out.write(filedata)
    tasks_sites.HOSTS = testfile
    assert tasks_sites.get_sitenames() == ['lemoncurry.nl', 'test.magiokis.nl']
