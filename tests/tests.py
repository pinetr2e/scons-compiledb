import subprocess
import json
import os
import pytest

TEST_ABSPATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def change_and_clean_dir():
    cmd = ';'.join(('cd {}'.format(TEST_ABSPATH),
                    'rm -f *.json .*.json *.o *.os hello* build/* build2/* '))
    subprocess.call(cmd, shell=True)


pytestmark = pytest.mark.usefixtures("change_and_clean_dir")


def run_scons(cmd):
    cmd = "{}".format(cmd)
    subprocess.check_output(cmd, shell=True)


def read_compile_db(db_name='compile_commands.json'):
    if not os.path.exists(db_name):
        return None

    with open(db_name) as f:
        return json.load(f)


def test_basic():
    run_scons('scons -f sconstruct_basic')
    db = read_compile_db()
    assert db == [
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o a.o -c -DD1 -II1 a.c",
            'file': 'a.c'
        },
        {
            'directory': TEST_ABSPATH,
            'command': "g++ -o b.o -c -DD1 -II1 b.cpp",
            'file': 'b.cpp'
        },
    ]
    run_scons('scons -f sconstruct_basic -c')
    assert not read_compile_db()


def test_enable_with_cmdline():
    run_scons('scons -f sconstruct_cmdline')
    assert read_compile_db() is None

    run_scons('scons -f sconstruct_cmdline --compiledb=')
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
            'directory': TEST_ABSPATH,
            'command': 'clang -DD1 -DD2 -II1 -II2 -c a.c',
            'file': 'a.c'
        },
        {
            'directory': TEST_ABSPATH,
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


def test_merge():
    run_scons('scons -f sconstruct_merge')
    run_scons('scons -f sconstruct_merge2')
    db = read_compile_db()
    assert db == [
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o a.o -c -DD1 -II1 a.c",
            'file': 'a.c'
        },
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o b.o -c -DD2 -II2 b.c",
            'file': 'b.c'
        },
    ]


def test_config_reset():
    run_scons('scons -f sconstruct_merge')
    run_scons('scons -f sconstruct_config_reset')
    db = read_compile_db()
    assert db == [
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o b.o -c -DD2 -II2 b.c",
            'file': 'b.c'
        },
    ]


def test_same_source_compiled_multiple_times():
    run_scons('scons -f sconstruct_same_source')
    db = read_compile_db()
    assert db == [
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o build2/a.o -c -DD2 a.c",
            'file': 'a.c'
        },
    ]


def test_config_multi():
    run_scons('scons -f sconstruct_config_multi')
    db = read_compile_db()
    assert db == [
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o build/a.o -c -DD1 a.c",
            'file': 'a.c'
        },
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o build2/a.o -c -DD2 a.c",
            'file': 'a.c'
        },
    ]


def test_enable_with_cmdline_with_config():
    run_scons('scons -f sconstruct_cmdline --compiledb=')
    assert read_compile_db() is not None

    run_scons('scons -f sconstruct_cmdline_config --compiledb=reset,multi')
    db = read_compile_db()
    assert db == [
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o build/b.o -c -DD1 b.c",
            'file': 'b.c'
        },
        {
            'directory': TEST_ABSPATH,
            'command': "gcc -o build2/b.o -c -DD2 b.c",
            'file': 'b.c'
        },
    ]
