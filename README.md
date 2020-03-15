# SCons Compilation DB support

scons-compiledb adds support for generating JSON formatted compilation database
defined by [Clang][https://clang.llvm.org/docs/JSONCompilationDatabase.html].

## Installation

Install and update using `pip`
```
pip install scons-compiledb
```

## Usage

```python
import scons-compiledb

env = DefaultEnvironment()
scons-compiledb.enable(env)

# ...
env.CompileDb()
```
