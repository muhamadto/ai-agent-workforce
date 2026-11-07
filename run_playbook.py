"""Supported credential-free local entry point for Shortcut 742."""
import argparse
import json
import os
from pathlib import Path
import re
import pwd
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
EXECUTION_PATH = '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
PLAYS = {'guidance':'deploy-pulumi-guidance.yml', 'workforce':'playbook.yml'}


def clean_environment(temporary):
    user = pwd.getpwuid(os.getuid())
    result = {'PATH':EXECUTION_PATH, 'HOME':user.pw_dir,
              'USER':user.pw_name, 'LOGNAME':user.pw_name, 'LANG':'C'}
    result.update({'ANSIBLE_CONFIG':str(ROOT/'ansible.cfg'),
                   'ANSIBLE_HOST_KEY_CHECKING': 'True',
                   'ANSIBLE_CACHE_PLUGIN':'memory',
                   'ANSIBLE_LOCAL_TEMP':str(Path(temporary)/'controller'),
                   'ANSIBLE_REMOTE_TEMP':str(Path(temporary)/'module'),
                   'ANSIBLE_NOCOLOR':'1'})
    return result


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'Invalid supported execution arguments\n')


def options(argv):
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('play', choices=PLAYS)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--diff', action='store_true')
    parser.add_argument('--tags')
    parser.add_argument('--skip-tags')
    result = parser.parse_args(argv)
    for field in ('tags','skip_tags'):
        value = getattr(result,field)
        if value is not None and not re.fullmatch(r'[A-Za-z0-9_,.-]+',value):
            parser.error('Invalid tag selection')
    return result


def main(argv=None):
    arguments = options(sys.argv[1:] if argv is None else argv)
    executable = shutil.which('ansible-playbook',path=EXECUTION_PATH)
    if not executable:
        print('Existing ansible-playbook is required',file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix='workforce-safe-') as temporary:
        inventory = Path(temporary)/'inventory.ini'
        inventory.write_text('[local]\nlocalhost ansible_connection=local\n')
        inventory.chmod(0o600)
        command = [executable,'--inventory',str(inventory),str(ROOT/PLAYS[arguments.play]),
                   '--extra-vars',json.dumps({'ansible_python_interpreter':sys.executable})]
        for option in ('check','diff'):
            if getattr(arguments,option):
                command.append('--'+option)
        for option in ('tags','skip_tags'):
            if getattr(arguments,option):
                command += ['--'+option.replace('_','-'),getattr(arguments,option)]
        try:
            return subprocess.run(command,cwd=ROOT,env=clean_environment(temporary),
                                  check=False).returncode
        except OSError:
            print('Local execution failed',file=sys.stderr)
            return 1

if __name__ == '__main__':
    sys.exit(main())
