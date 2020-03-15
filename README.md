# SCons Compilation DB support

scons-compiledb adds a support for generating JSON formatted compilation
database defined by
[Clang](https://clang.llvm.org/docs/JSONCompilationDatabase.html).

The main functionality of scons-compiledb is based on the version in
[MongoDB](https://github.com/mongodb/mongo/blob/master/site_scons/site_tools/compilation_db.py).

Features:

- Multiple construction environments support.
- Merging of compile_commands.json.
- Simple customisation for DB entry generation.
- DB generation with --compiledb command line option.
- Installation with PyPI



## Installation

Install and update using `pip`
```
pip install scons-compiledb
```

## Usage

In Scons script, enable generation:

```python
import scons_compiledb

env = DefaultEnvironment()  # Or with any other way
scons_compiledb.enable_cmdline(env)
#
# ... Use env normnally ...
#
```

Generate compile_commands.json by invoking SCons with --compiledb command line option:
```
$ scons --compiledb

...
Check compilation DB : compile_commands.json.pickle
Update compilation DB: compile_commands.json
scons: done building targets.
```
