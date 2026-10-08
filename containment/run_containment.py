"""Dedicated clean-environment entry point; no arbitrary Ansible options."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def clean_environment(temporary):
    # Only OS execution essentials; never forward credentials or Ansible overrides.
    result = {key: os.environ[key] for key in ('PATH', 'HOME', 'USER', 'LOGNAME', 'LANG')
              if key in os.environ}
    result.update({'ANSIBLE_CONFIG': str(HERE / 'ansible.cfg'),
                   'ANSIBLE_CACHE_PLUGIN': 'memory',
                   'ANSIBLE_GATHERING': 'explicit',
                   'ANSIBLE_LOCAL_TEMP': temporary,
                   'ANSIBLE_REMOTE_TEMP': temporary,
                   'ANSIBLE_NOCOLOR': '1'})
    return result


def main():
    if sys.argv[1:] not in ([], ['--check']):
        print('Only --check is accepted', file=sys.stderr)
        return 1
    executable = shutil.which('ansible-playbook')
    if not executable:
        print('Existing ansible-playbook is required', file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix='fact-cache-containment-') as temporary:
        command = [executable, '--inventory', 'localhost,', '--connection', 'local',
                   str(HERE / 'contain-fact-caches.yml'), '--extra-vars',
                   json.dumps({'containment_python': sys.executable,
                               'ansible_python_interpreter': sys.executable})]
        command += sys.argv[1:]
        try:
            return subprocess.run(command, env=clean_environment(temporary),
                                  cwd=HERE, check=False).returncode
        except OSError:
            print('Containment execution failed', file=sys.stderr)
            return 1

if __name__ == '__main__':
    sys.exit(main())
