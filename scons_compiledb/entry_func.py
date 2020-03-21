from SCons.Action import Action


def default(env, target, source, cxx, shared):
    """
    A default DB entry function which will work for the most of cases.
    """
    cmdstr = '${}{}'.format('SH' if shared else '',
                            'CXXCOM' if cxx else 'CCCOM')
    command = Action(cmdstr).strfunction(target, source, env)
    return {'directory': env.Dir('#').abspath,
            'file': str(source[0]),
            'command': command}


def simple(env, target, source, cxx, shared):
    """
    A simple DB entry function to pretend that the current tool chain uses
    clang/clang++.
    """
    flags = '{} {}'.format(
        ' '.join('-D{}'.format(d) for d in env.get('CPPDEFINES')),
        ' '.join('-I{}'.format(i) for i in env.get('CPPPATH')))
    source_path = source[0].path
    toolchain = 'clang++' if cxx else 'clang'
    return {'directory': env.Dir('#').abspath,
            'file': source_path,
            'command': '{} {} -c {}'.format(toolchain, flags, source_path)}
