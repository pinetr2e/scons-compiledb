from SCons.Action import Action


def default(env, target, source, cxx, shared):
    """
    A default DB entry function which will work for the most of cases.
    """
    s = '${}{}'.format('SH' if shared else '',
                       'CXXCOM' if cxx else 'CCCOM')
    command = Action(s).strfunction(target, source, env)
    return {'directory': env.Dir('#').abspath,
            'file': str(source[0]),
            'command': command}


def simple(env, target, source, cxx, shared):
    """
    A simple DB entry function to pretend that the current tool chain uses
    clang/clang++.
    """
    env = env.Override(dict(CPPDEFPREFIX='-D', CPPDEFSUFFIX='', INCPREFIX='-I',
                            INCSUFFIX=''))
    toolchain = 'clang++' if cxx else 'clang'
    s = toolchain + ' $_CPPDEFFLAGS $_CPPINCFLAGS -c $SOURCE'
    command = Action(s).strfunction(target, source, env)
    return {'directory': env.Dir('#').abspath,
            'file': str(source[0]),
            'command': '{}'.format(command)}
