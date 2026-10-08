"""Privatise only recognised caches; never emit their contents (Shortcut 742)."""
import ctypes
import errno
import json
import os
from pathlib import Path
import stat
import sys

MAX_BYTES = 16 * 1024 * 1024
ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ROOT / '.ansible/facts/s1_localhost',
    Path('/Users/matto/Workspace/ai-agent-workforce/.ansible/facts/s1_localhost'),
    Path('/private/tmp/ansible_facts/s1_localhost'),
)

class Refused(Exception):
    """Safe diagnostic deliberately contains no path, facts or exception text."""


def identity(info):
    return (info.st_dev, info.st_ino, info.st_uid, info.st_nlink,
            info.st_size, info.st_mtime_ns)


def no_acl(fd):
    if sys.platform != 'darwin':
        raise Refused('ACL inspection requires macOS')
    before = identity(os.fstat(fd))
    lib = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    lib.acl_get_fd_np.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.acl_get_fd_np.restype = ctypes.c_void_p
    lib.acl_get_entry.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_void_p)]
    lib.acl_get_entry.restype = ctypes.c_int
    lib.acl_free.argtypes = [ctypes.c_void_p]
    lib.acl_free.restype = ctypes.c_int
    ctypes.set_errno(0)
    acl = lib.acl_get_fd_np(fd, 0x100)  # macOS ACL_TYPE_EXTENDED
    if not acl:
        # Darwin returns ENOENT for an absent extended ACL. The file itself
        # must still exist unchanged on the exact descriptor.
        if ctypes.get_errno() != errno.ENOENT or identity(os.fstat(fd)) != before:
            raise Refused('ACL inspection failed')
        return
    try:
        entry = ctypes.c_void_p()
        result = lib.acl_get_entry(acl, 0, ctypes.byref(entry))
        # Darwin: 0 = entry retrieved, 1 = no more entries, -1 = error.
        if result != 1 or identity(os.fstat(fd)) != before:
            raise Refused('Extended ACL or ACL inspection failure')
    finally:
        lib.acl_free(acl)


def recognised(raw):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Refused('Duplicate cache key')
            result[key] = value
        return result
    try:
        outer = json.loads(raw, object_pairs_hook=unique_pairs)
        if not isinstance(outer, dict) or set(outer) != {'__payload__'}:
            return False
        if not isinstance(outer['__payload__'], str):
            return False
        facts = json.loads(outer['__payload__'], object_pairs_hook=unique_pairs)
        return (isinstance(facts, dict)
                and isinstance(facts.get('ansible_env'), dict)
                and isinstance(facts.get('ansible_python'), dict)
                and isinstance(facts.get('gather_subset'), list))
    except (ValueError, TypeError, RecursionError):
        return False


def contain(path, check=False):
    """FD-relative traversal; never follows links or chmods by pathname."""
    uid = os.getuid()
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise Refused('Unsafe cache path')
    opened = []
    chain = []
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        opened.append(parent)
        traversed = Path('/')
        for component in path.parts[1:-1]:
            traversed /= component
            try:
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=parent)
            except FileNotFoundError:
                return False
            opened.append(child)
            info = os.fstat(child)
            if info.st_uid not in (0, uid):
                raise Refused('Unexpected ancestor owner')
            if info.st_mode & 0o022:
                if not (traversed == Path('/private/tmp')
                        and info.st_uid == 0 and info.st_mode & stat.S_ISVTX):
                    raise Refused('Writable cache ancestor')
            chain.append((parent, component, identity(info)))
            parent = child
        try:
            fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=parent)
        except FileNotFoundError:
            return False
        opened.append(fd)
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != uid
                or before.st_nlink != 1 or before.st_size > MAX_BYTES):
            raise Refused('Unsafe cache file')
        no_acl(fd)
        raw = bytearray()
        while len(raw) <= MAX_BYTES:
            chunk = os.read(fd, min(65536, MAX_BYTES + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        if len(raw) > MAX_BYTES or not recognised(raw):
            raise Refused('Unrecognised cache file')
        if identity(os.fstat(fd)) != identity(before):
            raise Refused('Cache changed during inspection')
        def verify_path():
            for directory, name, expected in chain:
                if identity(os.stat(name, dir_fd=directory, follow_symlinks=False)) != expected:
                    raise Refused('Cache ancestor changed')
            if identity(os.stat(path.name, dir_fd=parent, follow_symlinks=False)) != identity(before):
                raise Refused('Cache path changed')
        verify_path()
        changed = stat.S_IMODE(before.st_mode) != 0o600
        if changed and not check:
            os.fchmod(fd, 0o600)
        after = os.fstat(fd)
        if identity(after) != identity(before):
            raise Refused('Cache changed during containment')
        no_acl(fd)
        verify_path()
        if not check and stat.S_IMODE(after.st_mode) != 0o600:
            raise Refused('Cache permissions not private')
        return changed
    except (OSError, ValueError, TypeError) as error:
        raise Refused('Cache containment refused') from error
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def main():
    if sys.argv[1:] not in ([], ['--check']):
        print('Invalid containment arguments', file=sys.stderr)
        return 1
    try:
        changes = sum(contain(target, '--check' in sys.argv) for target in TARGETS)
    except Refused:
        print('Cache containment refused; private review required', file=sys.stderr)
        return 1
    print('changed' if changes else 'unchanged')
    return 0

if __name__ == '__main__':
    sys.exit(main())
