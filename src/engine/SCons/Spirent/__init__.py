__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import hashlib
import json
import os.path
import time

import SCons.Action
import SCons.Node
import SCons.SConf

class GraphWriter(object):
    whitelist_funcs = {
        'LibSymlinksActionFunction',
        'SharedFlagChecker',
    }

    def __init__(self):
        self._env = None
        if os.path.sep != '/':
            self._path_transform = lambda x: x.replace(os.path.sep, '/')
        else:
            self._path_transform = lambda x: x

    def _get_node_cmdlines(self, node, act, target, source, env):
        if isinstance(act, SCons.Action.CommandAction):
            return [act.strfunction(target, source, env)]
        elif isinstance(act, SCons.Action.CommandGeneratorAction):
            return self._get_node_cmdlines(node, act._generate(target, source, env, 0), target, source, env)
        elif isinstance(act, SCons.Action.ListAction):
            cs = []
            for a in act.list:
                for c in self._get_node_cmdlines(node, a, target, source, env) or []:
                    if c is not None:
                        cs.append(c)
            return cs
        elif isinstance(act, SCons.Action.FunctionAction):
            f = str(act).split('(', 1)[0]
            # TODO: after SConscript rework is done, assert on function actions not whitelisted
            #if f not in self.whitelist_funcs:
            #    assert False, "unhandled SCons.Action.FunctionAction"
            return ["#" + f]
        else:
            assert False, "unhandled SCons.Action type"

    def _get_env_deltas(self, env):
        try:
            return dict((k, v) for (k, v) in env['ENV'].items() if not self._env or k not in self._env)
        except (TypeError, KeyError):
            return None

    def _get_node_hash(self, path):
        sha1 = hashlib.sha1()
        with open(path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    def _get_node_mode(self, path):
        return oct(os.stat(path).st_mode & 0777)

    def _write_derived_node(self, f, node_id, path, is_root):
        path = self._path_transform(path)
        attrs = 'type=derived,path=' + json.dumps(path)
        if is_root:
            attrs += ',root=true'
        f.write('  n%x [%s];\n' % (node_id, attrs))

    def _write_dir_node(self, f, node_id, path, is_root):
        path = self._path_transform(path)
        attrs = 'type=dir,path=' + json.dumps(path)
        if is_root:
            attrs += ',root=true'
        f.write('  n%x [%s];\n' % (node_id, attrs))

    def _write_builder_node(self, f, node_id, cmdlines, env):
        attrs = 'type=builder,cmdlines=' + json.dumps(json.dumps(cmdlines))
        if env:
            attrs += ',env=' + json.dumps(json.dumps(env))
        f.write('  n%x [%s];\n' % (node_id, attrs))

    def _write_source_node(self, f, node_id, path, sha1, mode):
        path = self._path_transform(path)
        attrs = 'type=source,path=' + json.dumps(path) + ',hash="' + sha1 + '"' + ',mode="' + mode + '"'
        f.write('  n%x [%s];\n' % (node_id, attrs))

    def _write_edge(self, f, from_id, to_id):
        if from_id:
            f.write('  n%x -> n%x;\n' % (from_id, to_id))

    def _walk_tree_write_nodes(self, f, parent_id, node, visited):
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)
        path = str(node)
        if node.has_builder():
            self._write_edge(f, parent_id, node_id)
            if not isinstance(node, SCons.Node.FS.Dir):
                self._write_derived_node(f, node_id, path, parent_id is None)
                act = node.builder.action
                target = [node]
                source = node.sources
                env = node.env or node.builder.env
                builder_id = abs(hash(str(act.get_presig(target, source, env))))
                if builder_id not in visited:
                    visited.add(builder_id)
                    cmdlines = self._get_node_cmdlines(node, act, target, source, env)
                    env = self._get_env_deltas(node.builder.env)
                    self._write_builder_node(f, builder_id, cmdlines, env)
                self._write_edge(f, node_id, builder_id)
                for child in node.all_children():
                    self._walk_tree_write_nodes(f, builder_id, child, visited)
            else:
                self._write_dir_node(f, node_id, path, parent_id is None)
                self._write_edge(f, parent_id, node_id)
                for child in node.all_children():
                    self._walk_tree_write_nodes(f, node_id, child, visited)
        elif isinstance(node, SCons.Node.FS.File) and node.exists() and not os.path.isabs(path):
            self._write_edge(f, parent_id, node_id)
            self._write_source_node(f, node_id, path, self._get_node_hash(path), self._get_node_mode(path))
            for child in node.all_children():
                self._walk_tree_write_nodes(f, node_id, child, visited)
        else:
            for child in node.all_children():
                self._walk_tree_write_nodes(f, parent_id, child, visited)

    def write(self, path, t):
        progress_display = SCons.SConf.progress_display
        progress_display("scons: writing build graph to %s." % path)
        start_time = time.time()

        try:
            self._env = dict((k, v) for (k, v) in t.builder.env['ENV'].items())
        except (TypeError, KeyError):
            pass

        # import cProfile, pstats, StringIO
        # pr = cProfile.Profile()
        # pr.enable()

        with open(path, 'w') as f:
            f.write('strict digraph {\n')
            if self._env:
                f.write('  graph [env=%s]\n' % json.dumps(json.dumps(dict(self._env))))
            self._walk_tree_write_nodes(f, None, t, set())
            f.write('}\n')

        # pr.disable()
        # s = StringIO.StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print s.getvalue()

        finish_time = time.time()
        progress_display("scons: took %f seconds to write build graph." % (finish_time-start_time))
