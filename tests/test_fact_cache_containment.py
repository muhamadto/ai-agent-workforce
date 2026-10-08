"""Synthetic caches only; never open the host's known cache files."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'containment' / 'contain_fact_caches.py'

class ContainmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('containment', SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name).resolve() / 's1_localhost'
        self.path.write_text(json.dumps({'__payload__': json.dumps({'ansible_env': {'SECRET': 'SYNTHETIC_SECRET'}, 'ansible_python': {'executable':'/fixture/python'}, 'gather_subset':['all']})}))
        self.path.chmod(0o644)

    def test_check_does_not_mutate_and_apply_is_idempotent(self):
        self.assertTrue(self.module.contain(self.path, check=True))
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o644)
        self.assertTrue(self.module.contain(self.path))
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertFalse(self.module.contain(self.path))
        self.assertIn('SYNTHETIC_SECRET', self.path.read_text())

    def assert_refused(self):
        for check in (True, False):
            with self.assertRaises(self.module.Refused):
                self.module.contain(self.path, check=check)

    def test_rejects_symlink_file(self):
        original = self.path.with_name('original')
        self.path.rename(original)
        self.path.symlink_to(original)
        self.assert_refused()
        self.assertEqual(original.stat().st_mode & 0o777, 0o644)

    def test_rejects_symlink_ancestor(self):
        link = self.path.parent / 'alias'
        link.symlink_to(self.path.parent, target_is_directory=True)
        self.path = link / self.path.name
        self.assert_refused()

    def test_rejects_hardlink(self):
        os.link(self.path, self.path.with_name('second'))
        self.assert_refused()

    def test_rejects_unknown_payload(self):
        self.path.write_text('{"secret": "SYNTHETIC_SECRET"}')
        self.assert_refused()

    def test_rejects_oversized_cache(self):
        with self.path.open('wb') as stream:
            stream.truncate(self.module.MAX_BYTES + 1)
        self.assert_refused()

    def test_rejects_foreign_owner(self):
        # Simulate the stat guard; changing a real owner would require privilege.
        with patch.object(self.module.os, 'getuid', return_value=os.getuid()+1):
            self.assert_refused()

    def test_rejects_extended_acl_on_real_fixture(self):
        import subprocess
        result = subprocess.run(['/bin/chmod', '+a', 'everyone allow read', str(self.path)], capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assert_refused()

    def test_rejects_directory(self):
        self.path.unlink()
        self.path.mkdir()
        self.assert_refused()

    def test_missing_cache_is_unchanged(self):
        self.path.unlink()
        self.assertFalse(self.module.contain(self.path))

    def test_refuses_path_replacement_before_mutation(self):
        real_acl = self.module.no_acl
        def replace_after_inspection(fd):
            real_acl(fd)
            self.path.rename(self.path.with_name('old'))
            self.path.write_text('replacement')
            self.path.chmod(0o644)
        with patch.object(self.module, 'no_acl', side_effect=replace_after_inspection):
            self.assert_refused()
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o644)

    def test_duplicate_keys_are_rejected(self):
        self.path.write_text('{"__payload__":"x", "__payload__":"y"}')
        self.assert_refused()

    def test_rejects_malformed_inner_json(self):
        self.path.write_text(json.dumps({'__payload__':'SYNTHETIC_SECRET'}))
        self.assert_refused()

    def test_rejects_fifo_without_blocking(self):
        self.path.unlink()
        os.mkfifo(self.path)
        self.assert_refused()

    def test_rejects_writable_ancestor(self):
        self.path.parent.chmod(0o777)
        self.assert_refused()

    def test_rejects_growth_during_read(self):
        read = self.module.os.read
        mutated = False
        def grow(fd, length):
            nonlocal mutated
            chunk = read(fd, length)
            if not mutated:
                with self.path.open('a') as stream:
                    stream.write(' ')
                mutated = True
            return chunk
        with patch.object(self.module.os, 'read', side_effect=grow):
            with self.assertRaises(self.module.Refused):
                self.module.contain(self.path)

    def test_cli_refusal_has_no_payload_or_traceback(self):
        import contextlib
        import io
        self.path.write_text('SYNTHETIC_SECRET')
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(self.module, 'TARGETS', (self.path,)), patch.object(self.module.sys, 'argv', ['contain']), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(self.module.main(), 1)
        self.assertNotIn('SYNTHETIC_SECRET', stdout.getvalue()+stderr.getvalue())
        self.assertNotIn('Traceback', stderr.getvalue())

    def test_refuses_ancestor_replacement_before_mutation(self):
        real_acl = self.module.no_acl
        folder = self.path.parent / 'cache'
        folder.mkdir()
        self.path.rename(folder / self.path.name)
        self.path = folder / self.path.name
        def replace_ancestor(fd):
            real_acl(fd)
            folder.rename(folder.with_name('retained'))
            folder.mkdir()
            self.path.write_text('replacement')
            self.path.chmod(0o644)
        with patch.object(self.module, 'no_acl', side_effect=replace_ancestor):
            with self.assertRaises(self.module.Refused):
                self.module.contain(self.path)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o644)

class LauncherTests(unittest.TestCase):
    def test_inherited_jsonfile_and_secret_are_not_forwarded(self):
        spec = importlib.util.spec_from_file_location('runner', SCRIPT.parent/'run_containment.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        with patch.dict(os.environ, {'ANSIBLE_CACHE_PLUGIN':'jsonfile', 'ANSIBLE_CONFIG':'/hostile/config', 'ANSIBLE_CALLBACK_PLUGINS':'/hostile/plugins', 'SANDPIPERS_SHORTCUT_API_TOKEN':'SYNTHETIC_SECRET'}):
            environment = runner.clean_environment('/private/fixture')
        self.assertEqual(environment['ANSIBLE_CACHE_PLUGIN'], 'memory')
        self.assertEqual(environment['ANSIBLE_CONFIG'], str(SCRIPT.parent/'ansible.cfg'))
        self.assertNotIn('ANSIBLE_CALLBACK_PLUGINS', environment)
        self.assertNotIn('SYNTHETIC_SECRET', repr(environment))

    def test_real_ansible_ignores_inherited_cache_and_secret(self):
        import subprocess
        spec = importlib.util.spec_from_file_location('runner', SCRIPT.parent/'run_containment.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory).resolve()
            cache = folder/'cache'
            cache.mkdir()
            play = folder/'fixture.yml'
            play.write_text('''---
- name: Synthetic clean execution
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Assert environment isolation in actual local child
      ansible.builtin.command:
        argv:
          - "{{ ansible_playbook_python }}"
          - -c
          - "import os; import ansible.constants as C; assert C.CACHE_PLUGIN == 'memory'; assert 'SANDPIPERS_SHORTCUT_API_TOKEN' not in os.environ"
      changed_when: false
''')
            with patch.dict(os.environ, {'ANSIBLE_CACHE_PLUGIN':'jsonfile', 'ANSIBLE_CACHE_PLUGIN_CONNECTION':str(cache), 'SANDPIPERS_SHORTCUT_API_TOKEN':'SYNTHETIC_SECRET', 'ANSIBLE_STDOUT_CALLBACK':'invalid_callback'}):
                environment = runner.clean_environment(str(folder/'tmp'))
                result = subprocess.run(['ansible-playbook', '-i', 'localhost,', '-c', 'local', str(play)], env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, 'Synthetic Ansible isolation fixture failed')
            self.assertNotIn('SYNTHETIC_SECRET', result.stdout+result.stderr)
            self.assertEqual(list(cache.iterdir()), [])
