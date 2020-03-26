import json
import itertools
import os

import SCons
from SCons.Builder import Builder, DictEmitter, ListEmitter
from SCons.Action import Action
from SCons.Script import GetOption, AddOption


def enable(env, config):
    compile_commands = {}
    merged_compile_commands = {}

    env['_COMPILE_DB_ID'] = id(compile_commands)
    entry_group = SCons.Node.Python.Value(id(compile_commands))

    def create_db_entry_emitter(cxx, shared):
        def emitter(target, source, env):
            if env.get('_COMPILE_DB_ID') != id(compile_commands):
                return target, source

            def add_db_entry():
                entry = config.entry_func(env, target, source, cxx, shared)
                if entry:
                    key = '{}:{}'.format(entry['file'], str(target[0]))
                    compile_commands[key] = entry

            entry_node = SCons.Node.Python.Value(source)
            entry = env._AddDbEntry(entry_node, [],
                                    _COMPILE_DB_ENTRY_FUNC=add_db_entry)
            env.AlwaysBuild(entry)
            env.NoCache(entry)
            env.Depends(entry_group, entry)
            return target, source
        return emitter

    def add_db_entry_action(target, source, env):
        env['_COMPILE_DB_ENTRY_FUNC']()

    def update_db_action(target, source, env):
        # Convert dict to a list sorted with file/output tuple.
        contents = [e for _, e in sorted(merged_compile_commands.items())]
        with open(target[0].path, 'w') as f:
            json.dump(contents, f, indent=2)

    def update_internal_db_action(target, source, env):
        merged_compile_commands.update(compile_commands)
        with open(target[0].path, 'w') as f:
            json.dump(merged_compile_commands, f, sort_keys=True)

    #
    # Hook new emitters to the existing ones
    #
    for ((cxx, suffix), shared) in itertools.product(
            [(True, s) for s in config.cxx_suffixes] +
            [(False, s) for s in config.cc_suffixes],
            (True, False)):
        builder = 'SharedObject' if shared else 'StaticObject'
        emitter = env['BUILDERS'][builder].emitter
        assert isinstance(emitter, DictEmitter)
        org = emitter[suffix]
        new = create_db_entry_emitter(cxx, shared)
        emitter[suffix] = ListEmitter((org, new))

    #
    # Add builders
    #
    env['BUILDERS']['_AddDbEntry'] = Builder(
        action=Action(add_db_entry_action, None))

    env['BUILDERS']['_UpdateInternalDb'] = Builder(
        action=Action(update_internal_db_action,
                      'Check compilation DB : $TARGET'))

    env['BUILDERS']['_UpdateDb'] = Builder(
        action=Action(update_db_action, 'Update compilation DB: $TARGET'))

    def compile_db(env, target=config.db):
        merged_compile_commands.clear()
        head, tail = os.path.split(target)
        internal_path = os.path.join(head, '.' + tail)
        internal_db = env._UpdateInternalDb(internal_path, entry_group)[0]
        if internal_db.exists():
            merged_compile_commands.update(
                json.loads(internal_db.get_text_contents()))
        env.AlwaysBuild(internal_db)
        return env._UpdateDb(target, internal_db)
    env.AddMethod(compile_db, 'CompileDb')


def enable_with_cmdline(env, config, option_name, option_help):
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

    enable(env, config)
    db = env.CompileDb(config.db)
    env.Default(env.Alias('compiledb', db))


def enabled(env):
    return '_UpdateDb' in env['BUILDERS']
