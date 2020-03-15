import subprocess
import json
import os
import pytest


@pytest.fixture
def cleandir():
    subprocess.call("cd tests; rm -f *.json *.pickle *.o *.os hello",
                    shell=True)


pytestmark = pytest.mark.usefixtures("cleandir")


def run_scons(cmd):
    cmd = "cd tests; {}".format(cmd)
    subprocess.check_output(cmd, shell=True)


def read_compile_db(db_name='compile_commands.json'):
    db_path = 'tests/{}'.format(db_name)
    if not os.path.exists(db_path):
        return None

    with open("tests/{}".format(db_name)) as f:
        items = json.load(f)
        return {i['file']: i for i in items}


def test_simple():
    run_scons('scons -f sconstruct_simple')
    db = read_compile_db()
    assert db['a.c']['command'] == "gcc -o a.o -c -DD1 -II1 a.c"
    assert db['a.c']['directory'] == os.path.abspath("tests")

    run_scons('scons -f sconstruct_simple -c')
    assert not read_compile_db()


def test_enable_with_cmdline():
    run_scons('scons -f sconstruct_cmdline')
    assert read_compile_db() is None

    run_scons('scons -f sconstruct_cmdline --compiledb')
    assert read_compile_db() is not None


def test_config_db():
    run_scons('scons -f sconstruct_config_db')
    assert read_compile_db('compile_commands.json') is None
    assert read_compile_db('foo.json') is not None


def test_config_entry_func():
    run_scons('scons -f sconstruct_config_entry_func')
    db = read_compile_db()
    assert db['a.c']['command'] == "clang -DD1 -DD2 -II1 -II2 -c a.c"
    assert db['a.c']['directory'] == "c:"
