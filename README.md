[![Build Status](https://travis-ci.org/pinetr2e/scons-compiledb.svg?branch=master)](https://travis-ci.org/pinetr2e/scons-compiledb)
[![PyPI version](https://badge.fury.io/py/scons-compiledb.svg)](https://badge.fury.io/py/scons-compiledb)
# SCons Compilation DB support

scons-compiledb adds a support for generating JSON formatted compilation
database defined by
[Clang](https://clang.llvm.org/docs/JSONCompilationDatabase.html).

Features:

- Multiple construction environments support.
- compile_commands.json merge across SCons invocations
- Customisation for DB entry generation.
- Build with command line option, --compiledb
- Simpler installation with PyPI


At the moment, SCons mainline does not have compilation DB generation
functionality and it is likely to have it in the near feature. However, this
module can still provide some advantages such as supporting old version of SCons
and other useful features.

The module was tested with Python 2.x/3.x along with SCons 2.x/3.x.


## Installation

Install and update using `pip`
```
pip install scons-compiledb
```

## Usage

### Enable and use CompileDb builder

```python
import scons_compiledb

env = DefaultEnvironment()  # Or with any other way
scons_compiledb.enable(env)
# 
# ... use env normally ...
#
env.CompileDb()
```

`enable(env)` adds a new builder, `CompileDb` to the specified environment,
`env`. In order to build the `compile_commands.json` file, `CompileDb()` should
be called. It can also specify the DB file name as an optional argument.

Note that `enable(env)` should be called before the `env` is used to compile any
targets.


### Simpler usage with command line option --compiledb

Instead of `enable()`, `enable_with_cmdline()` can be used to add a command line
option `--compiledb`, which, when specified, generates 'compile_commands.json'
as default target.

```python
import scons_compiledb

env = DefaultEnvironment()  # Or with any other way
scons_compiledb.enable_with_cmdline(env)

#
# ... Use env normnally ...
#
```

With the above build script, `compile_commands.json` file will be generated when
SCons is invoked with `--compiledb` command line option as follows:

```
$ scons --compiledb=
```
Note that the command line option requires an option string as argument and the trailing `=` means empty.
The comma-separated option string can specify the bool type config options(see below) as follows:
```
$ scons --compiledb=reset,multi
```

In order to build DB while building other target, `compiledb` can be used as an
alias as follows:

```
$ scons --compiledb= compiledb other_targets
```


### Customisation
While enabling, a `Config` object can be passed. For example:
```
config = scons_compiledb.Config(db='foo.json')
scons_compiledb.enable(env, config)

```

| Parameter    | Value                                                      | Default                   |
|--------------|------------------------------------------------------------|---------------------------|
| db           | filename of compilation DB.                                | '#/compile_commands.json' |
| entry_func   | function to determine the entry dict for each source file. | entry_func_default        |
| cxx_suffixes | Suffixes for C++ files.                                    | ('.cpp', '.cc')           |
| ccc_suffixes | Suffixes for C files.                                      | ('.c,)                    |
| reset        | Whether to remove existing entries                         | False                     |
| multi        | Whether to allow multiple entries with the same 'file'.    | False                     |

#### entry_func

`entry_func` is the main logic to convert source file node in SCons to a dict
 containing `directory`, `source` and `command` as keys. There are predefined
 entry functions as follows:

- `entry_func_default`

This is default and it should work for the most of cases.

- `entry_func_simple`

Use `CPPPATH` and `CPPDEFINES` only and *clang*/*clang++* as compiler tool name.
This will be useful to use clangd with compilers, which use command line
arguments clangd cannot understand.

`entry_func` can be easily customised. Please refer to the source code of [the
predefined functions](./scons_compiledb/entry_func.py)

#### reset

As default, `compile_commands.json` file is merged across the multiple
invocations of SCons so that one DB file can be used. This is usually good
thing. However, if it is not desirable for any reasons, `reset` config can be
used to remove any existing entries before generating new ones.

#### multi

As default, `compile_commands.json` file keeps only one entry with the same
`file` as the key. However, some tools can handle multiple entries with the same
key. If `multi` is set, multiple entries are stored as long as they generate the
different target(output) files.

## Details


`enable(env)` modifies the builders related to the compilations, such as
StaticObject, to add a additional Scanner, which make sure that the compilation
commands are captured. `enable(env)` also adds a new builder `CompileDb`, which
generates `compile_commands.json` from the captured commands.

`scons_compiledb` maintains an internal dot file `.compile_commands.json` as
default, to merge compile commands across the multiple SCons invocations. The
final file, `compile_commands.json` is touched only when the internal dot file
is changed.

When the compile commands are merged, it is based on source/output file name. It
means that the entry with the same pair will be overwritten.

`enabled(env)` can be called to check whether it is enabled before or not.


## Examples

Please check SConscript files in [test folder](./tests)


## Credits

The core functionality of scons-compiledb is based on [MongoDB source
code](https://github.com/mongodb/mongo/blob/master/site_scons/site_tools/compilation_db.py).
