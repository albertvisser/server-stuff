import os
import contextlib
import types
from invoke import MockContext
import tasks_sites as testee


def mock_run(self, *args):
    print(*args)


def mock_check(*args, **kwargs):
    print('called check_sites with args', *args, kwargs)


def mock_names(names):
    print(f"called names2sites with arg '{names}'")
    return names.split(',')


def test_list_domains(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'get_sitenames', lambda: ('name', 'another_name'))
    testee.list_domains(MockContext())
    assert capsys.readouterr().out == 'defined domains:\nname\nanother_name\n'


def test_check_up(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'check_sites', mock_check)
    testee.check_up(MockContext())
    assert capsys.readouterr().out == ("called check_sites with args"
                                       " {'up_only': True, 'sites': None}\n")


def test_check_all(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'check_sites', mock_check)
    testee.check_all(MockContext())
    assert capsys.readouterr().out == "called check_sites with args {}\n"


def test_check_pages(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'check_sites', mock_check)
    testee.check_pages(MockContext(), 'this,that')
    assert capsys.readouterr().out == ("called check_sites with args "
                                       "{'quick': False, 'sites': ['this', 'that']}\n")


def test_check_all_pages(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'check_sites', mock_check)
    testee.check_all_pages(MockContext())
    assert capsys.readouterr().out == ("called check_sites with args {'quick': False}\n")


def test_check_project_up(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'names2sites', mock_names)
    monkeypatch.setattr(testee, 'check_sites', mock_check)
    testee.check_project_up(MockContext(), 'sitenames')
    assert capsys.readouterr().out == ("called names2sites with arg 'sitenames'\n"
                                       "called check_sites with args"
                                       " {'up_only': True, 'sites': ['sitenames']}\n")


def test_check_project(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'names2sites', mock_names)
    monkeypatch.setattr(testee, 'check_sites', mock_check)
    testee.check_project(MockContext(), 'hello,world')
    assert capsys.readouterr().out == ("called names2sites with arg 'hello,world'\n"
                                       "called check_sites with args"
                                       " {'quick': False, 'sites': ['hello', 'world']}\n")


def test_names2sites():
    assert testee.names2sites('') == []
    assert testee.names2sites('this, that') == ['this.lemoncurry.nl', ' that.lemoncurry.nl']
    assert testee.names2sites('this,magiokis-test') == ['this.lemoncurry.nl', 'test.magiokis.nl']
    assert testee.names2sites('magiokis') == ['original.magiokis.nl', 'songs.magiokis.nl',
                                              'vertel.magiokis.nl', 'denk.magiokis.nl',
                                              'dicht.magiokis.nl']
    assert testee.names2sites('rst2html') == ['rst2html.lemoncurry.nl',
                                              'rst2html-mongo.lemoncurry.nl',
                                              'rst2html-pg.lemoncurry.nl']


def test_check_sites(monkeypatch, capsys):
    monkeypatch.setattr(testee, 'get_sitenames', lambda: ('name', 'another_name'))
    monkeypatch.setattr(testee, 'check_frontpage', lambda x: 201)
    testee.check_sites()
    assert capsys.readouterr().out == ('checking name... error 201\n'
                                       'checking another_name... error 201\n')
    monkeypatch.setattr(testee, 'get_sitenames', lambda: ('name', 'another_name'))
    testee.check_sites(sites=['name', 'not_a_name'])
    assert capsys.readouterr().out == ('checking name... error 201\n')
    monkeypatch.setattr(testee, 'check_frontpage', lambda x: 200)
    testee.check_sites(sites=['name'], up_only=True)
    assert capsys.readouterr().out == ('checking name... ok\n')
    testee.check_address = {'quick': {}}
    testee.check_sites(sites=['name'])
    assert capsys.readouterr().out == ('checking name... ok\n')
    testee.check_address = {'quick': {'name': 'page'}}
    monkeypatch.setattr(testee, 'check_page', lambda x: types.SimpleNamespace(status_code=201))
    testee.check_sites(sites=['name'], quick=True)
    assert capsys.readouterr().out == ('checking name... ok\n    error 201 on namepage\n')
    testee.check_address = {'full': {}}
    testee.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok\n'
                                       '    check_address entry missing for name\n')
    testee.check_address = {'full': {'name': ''}}
    testee.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok,'
                                       ' no further checking necessary\n')
    testee.check_address = {'full': {'name': 'name-urls'}}
    urlfiles_dir = os.path.expanduser(os.path.join('~', 'nginx-config', 'check-pages'))
    if os.path.exists(urlfiles_dir):
        with contextlib.suppress(FileNotFoundError):
            os.remove(os.path.join(urlfiles_dir, 'name-urls'))
    testee.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok\n'
                                       '    check-pages file missing for name\n')
    with contextlib.suppress(FileExistsError):
        os.mkdir(urlfiles_dir)
    with open(os.path.join(urlfiles_dir, 'name-urls'), 'w') as out:
        out.write('/testurl')
    testee.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok\n'
                                       '    checking name/testurl... error 201\n')
    monkeypatch.setattr(testee, 'check_page', lambda x: types.SimpleNamespace(status_code=200))
    testee.check_sites(sites=['name'], quick=False)
    assert capsys.readouterr().out == ('checking name... frontpage ok\n'
                                       '    checking name/testurl... ok\n')


def test_check_page(monkeypatch, capsys):
    def mock_get(*args, **kwargs):
        return args[0]
    monkeypatch.setattr(testee.requests, 'get', mock_get)
    assert testee.check_page('somesite') == 'http://somesite'


def test_check_frontpage(monkeypatch, capsys):
    def mock_check(*args):
        return types.SimpleNamespace(status_code=testee.HTTP_OK)
    monkeypatch.setattr(testee, 'check_page', mock_check)
    assert testee.check_frontpage('somesite') == testee.HTTP_OK


def test_get_sitenames(monkeypatch, capsys, tmp_path):
    filedata = ('xxx  lennoncurry\nxxx  lemoncurry.nl\nxx test.magiokis.nl\n'
                '# deze regel niet laten zien\nxxx  jansen')
    testfile = tmp_path / 'hoststest'
    testfile.write_text(filedata)
    testee.HOSTS = testfile
    assert testee.get_sitenames() == ['lemoncurry.nl', 'test.magiokis.nl']
