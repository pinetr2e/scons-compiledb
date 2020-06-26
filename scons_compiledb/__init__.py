from . import core, cmdline, entry_func

__version__ = '0.7.4'

DEFAULT_OPTION_NAME = 'compiledb'
DEFAULT_DB_NAME = '#/compile_commands.json'


def enable(env, config=None):
    """
    Enable compilation command collection by hooking into object builders.

    enable() adds a new builder, CompileDb to generates DB file. CompileDb
    builder can specify the target DB file and the default is
    'compile_commands.json'.

    Note that CompileDb builder only collects info for the object builders
    since enable() is called.
    """
    return core.enable(env, config if config else Config())


def enable_with_cmdline(env, config=None,
                        option_name=DEFAULT_OPTION_NAME):
    """
    Enable and build DB with command line option, --compiledb=.
    """
    return cmdline.enable_with_cmdline(
        env, config if config else Config(), option_name)


entry_func_simple = entry_func.simple
entry_func_default = entry_func.default


class Config:
    """
    Customise the overall behaviour.

    - db           : file name of compilation DB.
    - cxx_suffixes : Suffixes for C++ files. Default is ('.cpp', and '.cc').
    - cc_suffixes  : Suffixes if C files. Default is ('.c',).
    - entry_func   : a function to determine the entry dict for each file.
        Predefined functions or a user-defined function can be used.
        It includes:

        - 'entry_func_default': This is default and it should work for most of
          cases

        - 'entry_func_simple': Use CPPPATH and CPPDEFINES only and
          'clang'/'clang++' as compiler tool name. This will be useful to use
          clangd with compilers, which use command line arguments clangd cannot
          understand.
     - reset       : Whether to reset old entries before collecting.
     - multi       : Whether to have multiple entries with the same 'file'.
    """

    def __init__(self,
                 db=DEFAULT_DB_NAME,
                 cxx_suffixes=('.cpp', '.cc'),
                 cc_suffixes=('.c',),
                 entry_func=entry_func_default,
                 reset=False,
                 multi=False):
        self.db = db
        self.cc_suffixes = cc_suffixes
        self.cxx_suffixes = cxx_suffixes
        self.entry_func = entry_func
        self.reset = reset
        self.multi = multi


def enabled(env):
    return core.enabled(env)
