# Copyright 2020 Hans Jang.
# Copyright 2015 MongoDB Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import itertools
import os

import SCons
from SCons.Builder import Builder, DictEmitter, ListEmitter
from SCons.Action import Action


class _EntryCounter:
    """
    Track original entries to decide the correct number of added/updated ones.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self._updated = {}

    def __str__(self):
        added = [k for k, (org, _) in self._updated.items() if not org]
        updated = [k for k, (org, new) in self._updated.items()
                   if org and org != new]
        return '{} added / {} updated'.format(len(added), len(updated))

    def update(self, key, old, new):
        if key in self._updated:
            org, _ = self._updated[key]
            if org == new:
                del self._updated[key]
            else:
                self._updated[key] = (org, new)
        else:
            self._updated[key] = (old, new)


def enable(env, config):
    compile_commands = {}
    entry_counter = _EntryCounter()

    env['_COMPILE_DB_ID'] = id(compile_commands)
    env['_COMPILE_DB_COUNTER'] = entry_counter

    entry_group = SCons.Node.Python.Value(id(compile_commands))

    def create_db_entry_emitter(cxx, shared):
        def emitter(target, source, env):
            if env.get('_COMPILE_DB_ID') != id(compile_commands):
                return target, source

            def add_db_entry():
                entry = config.entry_func(env, target, source, cxx, shared)
                if entry:
                    key = '{}:{}'.format(
                        entry['file'], str(target[0]) if config.multi else '')
                    old_entry = compile_commands.get(key)
                    compile_commands[key] = entry
                    entry_counter.update(key, old_entry, entry)

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
        contents = [e for _, e in sorted(compile_commands.items())]
        with open(target[0].path, 'w') as f:
            json.dump(contents, f, indent=2)

    def update_internal_db_action(target, source, env):
        with open(target[0].path, 'w') as f:
            json.dump(compile_commands, f, indent=2, sort_keys=True)

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
                      'Check compilation DB : $TARGET ... '
                      '$_COMPILE_DB_COUNTER'))

    env['BUILDERS']['_UpdateDb'] = Builder(
        action=Action(update_db_action,
                      'Update compilation DB : $TARGET'))

    def compile_db(env, target=config.db):
        compile_commands.clear()
        entry_counter.reset()
        head, tail = os.path.split(target)
        internal_path = os.path.join(head, '.' + tail)
        internal_db = env._UpdateInternalDb(internal_path, entry_group)[0]
        if (not config.reset) and internal_db.exists():
            compile_commands.update(
                json.loads(internal_db.get_text_contents()))
        env.AlwaysBuild(internal_db)
        return env._UpdateDb(target, internal_db)
    env.AddMethod(compile_db, 'CompileDb')


def enabled(env):
    return '_UpdateDb' in env['BUILDERS']
