from SCons.Script import GetOption, AddOption
from . import core

DEFAULT_OPTION_NAME = 'compiledb'


def enable_with_cmdline(env, config=None,
                        option_name=DEFAULT_OPTION_NAME,
                        option_help='Update {}'.format(core.DEFAULT_DB_NAME)):
    """
    Add command line option(--compiledb) and build DB if it is set.
    """
    config = config if config else core.Config()

    def is_option_on():
        def add_script_option():
            AddOption('--' + option_name, dest='compile_db',
                      action='store_true', help=option_help)
        try:
            return GetOption('compile_db')
        except AttributeError:
            add_script_option()
            return GetOption('compile_db')

    if not is_option_on():
        return

    core.enable(env, config)
    db = env.CompileDb(config.db)
    env.Default(db)
