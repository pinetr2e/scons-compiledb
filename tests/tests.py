import subprocess
import json
import os
import pytest


@pytest.fixture
def cleandir():
    subprocess.call(
        "cd tests; rm -f *.json *.pickle *.o *.os hello* build/* build2/* ",
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
        return json.load(f)


def test_basic():
    run_scons('scons -f sconstruct_basic')
    db = read_compile_db()
    assert db == [
        {
            'directory': os.path.abspath("tests"),
            'command': "gcc -o a.o -c -DD1 -II1 a.c",
            'file': 'a.c'
        },
        {
            'directory': os.path.abspath("tests"),
            'command': "g++ -o b.o -c -DD1 -II1 b.cpp",
            'file': 'b.cpp'
        },
    ]
    run_scons('scons -f sconstruct_basic -c')
    assert not read_compile_db()


def test_same_source_compiled_multiple_times():
    run_scons('scons -f sconstruct_same_source')
    db = read_compile_db()
    assert db == [
        {
            'directory': os.path.abspath("tests"),
            'command': "gcc -o build/a.o -c -DD1 a.c",
            'file': 'a.c'
        },
        {
            'directory': os.path.abspath("tests"),
            'command': "gcc -o build2/a.o -c -DD2 a.c",
            'file': 'a.c'
        },
    ]
    run_scons('scons -f sconstruct_basic -c')
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


def test_config_entry_func_simple():
    run_scons('scons -f sconstruct_config_entry_func_simple')
    db = read_compile_db()
    assert db == [
        {
            'directory': os.path.abspath("tests"),
            'command': 'clang -DD1 -DD2 -II1 -II2 -c a.c',
            'file': 'a.c'
        },
        {
            'directory': os.path.abspath("tests"),
            'command': 'clang++ -DD1 -DD2 -II1 -II2 -c b.cpp',
            'file': 'b.cpp'
        },
    ]


def test_config_custom_entry_func():
    run_scons('scons -f sconstruct_config_custom_entry_func')
    db = read_compile_db()
    assert db == [
        {
            'directory': "c:",  # Changed
            'command': 'clang -DD1 -DD2 -II1 -II2 -c a.c',
            'file': 'a.c'
        }
    ]


def test_multiple_envs():
    run_scons('scons -f sconstruct_multiple_envs')
    db = read_compile_db('foo.json')
    assert db == [
        {
            'directory': os.path.abspath("tests"),
            'command': "gcc -o a.o -c -DD1 -II1 a.c",
            'file': 'a.c'
            }
    ]
    db2 = read_compile_db('bar.json')
    assert db2 == [
        {
            'directory': os.path.abspath("tests"),
            'command': "gcc -o b.o -c -DD2 -II2 b.c",
            'file': 'b.c'
        }
    ]
