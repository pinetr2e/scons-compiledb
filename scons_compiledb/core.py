import json
import os
import pickle
import itertools

import SCons
from SCons.Builder import Builder, DictEmitter, ListEmitter
from SCons.Action import Action

DEFAULT_DB_NAME = 'compile_commands.json'


def _create_db_entry(env, target, source, cxx, shared):
    cmdstr = '${}{}'.format('SH' if shared else '',
                            'CXXCOM' if cxx else 'CCCOM')
    command = Action(cmdstr).strfunction(target, source, env)
    return {'directory': env.Dir('#').abspath,
            'file': str(source[0]),
            'command': command}


class Config:
    def __init__(self,
                 db=DEFAULT_DB_NAME,
                 cxx_suffixes=('.cpp', '.cc'),
                 cc_suffixes=('.c',),
                 entry_func=_create_db_entry):
        self.db = db
        self.cc_suffixes = cc_suffixes
        self.cxx_suffixes = cxx_suffixes
        self.entry_func = entry_func


def enable(env, config=None):
    """
    Hook into object builders to collect compilation info.

    enable() adds a new builder, CompileDb to generates DB file. CompileDb
    builder can specify the target DB file and the default is
    compile_commands.json.

    Note that CompileDb builder only collects info for the object builders
    since enable() is called.
    """
    config = config if config else Config()
    compile_commands = {}
    db_entry_nodes = []

    env['_COMPILE_DB_ID'] = id(compile_commands)

    def create_db_entry_emitter(cxx, shared):
        def emitter(target, source, env):
            if env.get('_COMPILE_DB_ID') != id(compile_commands):
                return target, source

            def add_db_entry():
                entry = config.entry_func(env, target, source, cxx, shared)
                if entry:
                    compile_commands[entry['file']] = entry

            entry_node = SCons.Node.Python.Value(source)
            entry = env._AddDbEntry(entry_node, [],
                                    _COMPILE_DB_ENTRY_FUNC=add_db_entry)
            env.AlwaysBuild(entry)
            env.NoCache(entry)
            db_entry_nodes.append(entry_node)
            return target, source
        return emitter

    def add_db_entry_action(target, source, env):
        env['_COMPILE_DB_ENTRY_FUNC']()

    def update_db_action(target, source, env):
        pickle_path = source[0].path
        dbPath = target[0].path
        with open(pickle_path, 'rb') as f:
            full_compile_commands = pickle.load(f)

        # Convert dict into a list
        contents = [dict(entry, file=source_file)
                    for source_file, entry in full_compile_commands.items()]
        with open(dbPath, 'w') as f:
            json.dump(contents, f, indent=2)

    def update_db_pickle_action(target, source, env):
        pickle_path = target[0].path
        full_compile_commands = {}
        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as f:
                full_compile_commands = pickle.load(f)
        full_compile_commands.update(compile_commands)
        with open(pickle_path, 'wb') as f:
            pickle.dump(full_compile_commands, f)

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

    env['BUILDERS']['_UpdateDbPickle'] = Builder(
        action=Action(update_db_pickle_action,
                      'Check compilation DB : $TARGET'),
        target_scanner=SCons.Scanner.Scanner(
            function=lambda node, env, path: db_entry_nodes,
            node_class=None))

    env['BUILDERS']['_UpdateDb'] = Builder(
        action=Action(update_db_action, 'Update compilation DB: $TARGET'))

    def compile_db(env, target=config.db):
        db_pickle = env._UpdateDbPickle('{}.pickle'.format(target), [])
        env.AlwaysBuild(db_pickle)
        return env._UpdateDb(target, db_pickle)
    env.AddMethod(compile_db, 'CompileDb')
