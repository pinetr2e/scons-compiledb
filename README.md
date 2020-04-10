[![Build Status](https://travis-ci.org/pinetr2e/scons-compiledb.svg?branch=master)](https://travis-ci.org/pinetr2e/scons-compiledb)
[![PyPI version](https://badge.fury.io/py/scons-compiledb.svg)](https://badge.fury.io/py/scons-compiledb)
# SCons Compilation DB support

scons-compiledb adds a support for generating JSON formatted compilation
database defined by
[Clang](https://clang.llvm.org/docs/JSONCompilationDatabase.html).

Features:

- Multiple construction environments support.
- Merge of compile_commands.json across SCons invocations
- Customisation for DB entry generation.
- Build with command line option, --compiledb
- Installation with PyPI


At the moment, SCons mainline does not have compilation DB generation
functionality and it is likely to have it in the near feature. However, this
module can still provide some advantages such as supporting old version of SCons
and other unique features.

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
...
env.CompileDb()
```

`enable(env)` adds a new builder, `CompileDb` to the specified environment,
`env`. In order to build the `compile_commands.json` file, `CompileDb()` should
be called. It can also specify the DB file name as an optional argument.


### Enable and generation with command line option --compiledb

Similar to above but, `enable_with_cmdline()` is used instead. It will build
'compile_commands.json' as default target with 'compildb' as alias name.

```python
import scons_compiledb

env = DefaultEnvironment()  # Or with any other way
scons_compiledb.enable_with_cmdline(env)
#
# ... Use env normnally ...
#
```
It means that `compile_commands.json` file will be generated when SCons is invoked with
`--compiledb` command line option as follows:

```
$ scons --compiledb

...
Check compilation DB : compile_commands.json.internal
Update compilation DB: compile_commands.json
scons: done building targets.
```

As alias, `compiledb` can be specified with other build targets as follows:
```
$ scons --compiledb other_targets compiledb
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

The main functionality of scons-compiledb is heavily based on [MongoDB source
code](https://github.com/mongodb/mongo/blob/master/site_scons/site_tools/compilation_db.py).
