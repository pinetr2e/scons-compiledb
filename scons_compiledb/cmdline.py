from SCons.Script import GetOption, AddOption
from . import core


_HELP = ' '.join((
    "Generate compilation database file",
    "OPTIONS is empty or comma-separated string of the following:",
    "'reset' to reset old entries.",
    "'multi' to allow multiple entries having the same file key."))

_OPTIONS = ('multi', 'reset')


def enable_with_cmdline(env, config, option_name):
    def get_option():
        try:
            return GetOption('compile_db')
        except AttributeError:
            AddOption('--' + option_name, dest='compile_db',
                      metavar='OPTIONS', help=_HELP)
            return GetOption('compile_db')
    option_str = get_option()
    if option_str is None:
        return

    # Apply options to config
    for bool_option in option_str.split(','):
        if bool_option in _OPTIONS:
            setattr(config, bool_option, True)
        elif bool_option:
            raise RuntimeError(
                "Unknown option: '{}'. It should be one of {}".format(
                    bool_option, _OPTIONS))

    core.enable(env, config)
    db = env.CompileDb(config.db)
    env.Default(env.Alias('compiledb', db))
