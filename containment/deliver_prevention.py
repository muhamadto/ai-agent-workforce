"""Narrow reviewed source rewrites; never run roles or install packages (742)."""
import ctypes
import errno
import hashlib
import re
import json
import os
from pathlib import Path
import secrets
import stat
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contain_fact_caches import Refused, identity, no_acl

ROOTS = (Path('/Users/matto/Workspace/ai-agent-workforce'),
         Path('/Users/matto/Workspace/mac-setup'))
FIXED_TARGETS = (
    ROOTS[0]/'ansible.cfg', ROOTS[0]/'playbook.yml',
    ROOTS[1]/'ansible.cfg', ROOTS[1]/'playbook.yml',
    ROOTS[1]/'roles/git/tasks/main.yml', ROOTS[1]/'roles/devtools/tasks/main.yml',
    ROOTS[1]/'roles/ai/tasks/ollama.yml',
    ROOTS[1]/'roles/security_checks/tasks/persistence_audit.yml',
)
CREATE_SOURCES = {
    ROOTS[0]/'run_playbook.py': Path(__file__).resolve().parents[1]/'run_playbook.py',
    ROOTS[1]/'run_playbook.py': Path(__file__).resolve().parents[2]/'mac-setup-k3d/run_playbook.py',
}
FIXED_TARGETS += tuple(CREATE_SOURCES)
MAX_BYTES = 2 * 1024 * 1024


def sha(value):
    return hashlib.sha256(value).hexdigest()


def read(fd):
    os.lseek(fd,0,os.SEEK_SET)
    data=bytearray()
    while len(data)<=MAX_BYTES:
        chunk=os.read(fd,min(65536,MAX_BYTES+1-len(data)))
        if not chunk:break
        data.extend(chunk)
    if len(data)>MAX_BYTES:raise Refused('Oversized source')
    return bytes(data)


def safe_directory_acl(fd):
    """Deny-only ancestor ACLs cannot grant a competing writer access."""
    if sys.platform!='darwin':raise Refused('Directory ACL inspection requires macOS')
    before=dir_identity(os.fstat(fd))
    lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True)
    lib.acl_get_fd_np.argtypes=[ctypes.c_int,ctypes.c_int];lib.acl_get_fd_np.restype=ctypes.c_void_p
    lib.acl_get_entry.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_void_p)]
    lib.acl_get_entry.restype=ctypes.c_int
    lib.acl_get_tag_type.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_int)]
    lib.acl_get_tag_type.restype=ctypes.c_int
    lib.acl_free.argtypes=[ctypes.c_void_p];lib.acl_free.restype=ctypes.c_int
    lib.acl_valid.argtypes=[ctypes.c_void_p];lib.acl_valid.restype=ctypes.c_int
    ctypes.set_errno(0);acl=lib.acl_get_fd_np(fd,0x100)
    if not acl:
        if ctypes.get_errno()!=errno.ENOENT or dir_identity(os.fstat(fd))!=before:
            raise Refused('Directory ACL inspection failed')
        return
    try:
        if lib.acl_valid(acl)!=0:raise Refused('Invalid directory ACL')
        for index in range(170):
            entry=ctypes.c_void_p();ctypes.set_errno(0)
            result=lib.acl_get_entry(acl,index,ctypes.byref(entry))
            # Darwin uses -1/EINVAL at the end of a validated ACL.
            if result==-1 and ctypes.get_errno()==errno.EINVAL:break
            if result!=0:raise Refused('Directory ACL inspection failed')
            tag=ctypes.c_int()
            if lib.acl_get_tag_type(entry,ctypes.byref(tag))!=0 or tag.value!=2:
                raise Refused('Directory ACL grants access')
        else:raise Refused('Excessive directory ACL entries')
        if dir_identity(os.fstat(fd))!=before:raise Refused('Directory changed')
    finally:lib.acl_free(acl)


def dir_identity(info):
    return info.st_dev,info.st_ino,info.st_uid,stat.S_IMODE(info.st_mode)


def deliver(spec,check=False):
    path=Path(spec['path'])
    if not path.is_absolute() or '..' in path.parts:raise Refused('Unsafe source path')
    if 'source' in spec:
        return create_launcher(spec,check)
    descriptors=[];chain=[];stage=None;out=None
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);descriptors.append(parent)
        safe_directory_acl(parent)
        for component in path.parts[1:-1]:
            child=os.open(component,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            descriptors.append(child);info=os.fstat(child)
            safe_directory_acl(child)
            if info.st_uid not in (0,os.getuid()) or info.st_mode & 0o022:
                raise Refused('Unsafe source ancestor')
            chain.append((parent,component,dir_identity(info)));parent=child
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);descriptors.append(fd)
        before=os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid()
                or before.st_nlink!=1 or before.st_size>MAX_BYTES):
            raise Refused('Unsafe source file')
        no_acl(fd)
        content=read(fd)
        if identity(os.fstat(fd))!=identity(before):raise Refused('Source changed')
        current=sha(content)
        if current==spec['after_sha256']:
            for directory,name,expected in chain:
                safe_directory_acl(directory)
                if dir_identity(os.stat(name,dir_fd=directory,follow_symlinks=False))!=expected:
                    raise Refused('Source ancestor changed')
                safe_directory_acl(directory)
            if identity(os.stat(path.name,dir_fd=parent,follow_symlinks=False))!=identity(before):
                raise Refused('Source path changed')
            safe_directory_acl(parent)
            return False
        if current!=spec['before_sha256']:raise Refused('Unknown source content')
        desired=content
        for replacement in spec['replacements']:
            old=replacement['before'].encode();new=replacement['after'].encode()
            if not old or desired.count(old)!=replacement['count']:
                raise Refused('Source replacement mismatch')
            desired=desired.replace(old,new)
        if sha(desired)!=spec['after_sha256']:raise Refused('Unreviewed source result')
        def revalidate():
            safe_directory_acl(parent)
            for directory,name,expected in chain:
                safe_directory_acl(directory)
                if dir_identity(os.stat(name,dir_fd=directory,follow_symlinks=False))!=expected:
                    raise Refused('Source ancestor changed')
            if identity(os.stat(path.name,dir_fd=parent,follow_symlinks=False))!=identity(before):
                raise Refused('Source path changed')
            if identity(os.fstat(fd))!=identity(before) or sha(read(fd))!=current:
                raise Refused('Source content changed')
            no_acl(fd)
        revalidate()
        if check:return True
        stage='.prevention-'+secrets.token_hex(16)
        out=os.open(stage,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
        descriptors.append(out)
        view=memoryview(desired)
        while view:
            count=os.write(out,view)
            if count<=0:raise Refused('Source staging failed')
            view=view[count:]
        os.fchown(out,-1,before.st_gid)
        os.fchmod(out,stat.S_IMODE(before.st_mode));os.fsync(out);no_acl(out)
        staged=os.fstat(out)
        if (staged.st_uid!=os.getuid() or staged.st_gid!=before.st_gid
                or staged.st_nlink!=1 or sha(read(out))!=spec['after_sha256']):
            raise Refused('Source staging changed')
        revalidate()
        if identity(os.stat(stage,dir_fd=parent,follow_symlinks=False))!=identity(staged):
            raise Refused('Source staging path changed')
        os.replace(stage,path.name,src_dir_fd=parent,dst_dir_fd=parent);stage=None
        installed=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        if identity(installed)!=identity(os.fstat(out)) or sha(read(out))!=spec['after_sha256']:
            raise Refused('Source publication changed')
        no_acl(out)
        for directory,name,expected in chain:
            safe_directory_acl(directory)
            if dir_identity(os.stat(name,dir_fd=directory,follow_symlinks=False))!=expected:
                raise Refused('Published ancestor changed')
        safe_directory_acl(parent)
        if identity(os.stat(path.name,dir_fd=parent,follow_symlinks=False))!=identity(os.fstat(out)):
            raise Refused('Published path changed')
        return True
    except (OSError,ValueError,KeyError,TypeError) as error:
        raise Refused('Source delivery refused') from error
    finally:
        if stage is not None and out is not None:
            try:
                candidate=os.stat(stage,dir_fd=parent,follow_symlinks=False)
                if (candidate.st_dev,candidate.st_ino)==(os.fstat(out).st_dev,os.fstat(out).st_ino):
                    os.unlink(stage,dir_fd=parent)
            except FileNotFoundError:
                pass
        for descriptor in reversed(descriptors):os.close(descriptor)


def create_launcher(spec,check=False):
    path=Path(spec['path']);source=Path(spec['source'])
    descriptors=[];chain=[];stage=None;out=None
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);descriptors.append(parent)
        safe_directory_acl(parent)
        for component in path.parts[1:-1]:
            child=os.open(component,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            descriptors.append(child);info=os.fstat(child)
            safe_directory_acl(child)
            if info.st_uid not in (0,os.getuid()) or info.st_mode & 0o022:
                raise Refused('Unsafe launcher ancestor')
            chain.append((parent,component,dir_identity(info)));parent=child
        def check_chain():
            safe_directory_acl(parent)
            for directory,name,expected in chain:
                safe_directory_acl(directory)
                if dir_identity(os.stat(name,dir_fd=directory,follow_symlinks=False))!=expected:
                    raise Refused('Launcher ancestor changed')
        try:
            existing=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
        except FileNotFoundError:
            existing=None
        if existing is not None:
            descriptors.append(existing);before=os.fstat(existing)
            if (not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid()
                    or before.st_nlink!=1 or before.st_size>MAX_BYTES):
                raise Refused('Unsafe existing launcher')
            no_acl(existing)
            if sha(read(existing))!=spec['after_sha256']:
                raise Refused('Unknown existing launcher')
            check_chain()
            if (identity(os.fstat(existing))!=identity(before)
                    or identity(os.stat(path.name,dir_fd=parent,follow_symlinks=False))!=identity(before)):
                raise Refused('Launcher changed')
            safe_directory_acl(parent)
            return False
        incoming=os.open(source,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK);descriptors.append(incoming)
        initial=os.fstat(incoming)
        if (not stat.S_ISREG(initial.st_mode) or initial.st_uid!=os.getuid()
                or initial.st_nlink!=1 or initial.st_size>MAX_BYTES):
            raise Refused('Unsafe launcher source')
        no_acl(incoming);desired=read(incoming)
        if sha(desired)!=spec['after_sha256'] or identity(os.fstat(incoming))!=identity(initial):
            raise Refused('Unreviewed launcher source')
        check_chain()
        if check:return True
        stage='.prevention-'+secrets.token_hex(16)
        out=os.open(stage,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
        descriptors.append(out)
        view=memoryview(desired)
        while view:
            count=os.write(out,view)
            if count<=0:raise Refused('Launcher staging failed')
            view=view[count:]
        os.fsync(out);no_acl(out);staged=os.fstat(out)
        if (staged.st_uid!=os.getuid() or staged.st_nlink!=1
                or sha(read(out))!=spec['after_sha256']):raise Refused('Launcher staging changed')
        check_chain()
        if identity(os.stat(stage,dir_fd=parent,follow_symlinks=False))!=identity(staged):
            raise Refused('Launcher staging path changed')
        # link is an atomic absent-only publication; never overwrite an owner file.
        os.link(stage,path.name,src_dir_fd=parent,dst_dir_fd=parent,follow_symlinks=False)
        published=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        if (published.st_dev,published.st_ino)!=(staged.st_dev,staged.st_ino):
            raise Refused('Launcher publication changed')
        os.unlink(stage,dir_fd=parent);stage=None
        if os.fstat(out).st_nlink!=1 or sha(read(out))!=spec['after_sha256']:
            raise Refused('Launcher publication changed')
        no_acl(out)
        for directory,name,expected in chain:
            safe_directory_acl(directory)
            if dir_identity(os.stat(name,dir_fd=directory,follow_symlinks=False))!=expected:
                raise Refused('Published ancestor changed')
        safe_directory_acl(parent)
        if identity(os.stat(path.name,dir_fd=parent,follow_symlinks=False))!=identity(os.fstat(out)):
            raise Refused('Published path changed')
        return True
    except (OSError,ValueError,KeyError,TypeError) as error:
        raise Refused('Launcher delivery refused') from error
    finally:
        if stage is not None and out is not None:
            try:
                candidate=os.stat(stage,dir_fd=parent,follow_symlinks=False)
                if (candidate.st_dev,candidate.st_ino)==(os.fstat(out).st_dev,os.fstat(out).st_ino):
                    os.unlink(stage,dir_fd=parent)
            except FileNotFoundError:
                pass
        for descriptor in reversed(descriptors):os.close(descriptor)


def validate_plan(specs):
    if not isinstance(specs,list) or len(specs)!=len(FIXED_TARGETS):raise Refused('Invalid source plan')
    for spec,target in zip(specs,FIXED_TARGETS):
        if not isinstance(spec,dict) or spec.get('path')!=str(target):raise Refused('Invalid source target')
        if not isinstance(spec.get('after_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',spec['after_sha256']):raise Refused('Invalid source digest')
        if target in CREATE_SOURCES:
            if set(spec)!={'path','source','after_sha256'} or spec['source']!=str(CREATE_SOURCES[target]):raise Refused('Invalid launcher source')
        else:
            if set(spec)!={'path','before_sha256','after_sha256','replacements'} or not isinstance(spec['before_sha256'],str) or not re.fullmatch('[0-9a-f]{64}',spec['before_sha256']):raise Refused('Invalid source digest')
            if not isinstance(spec['replacements'],list) or not spec['replacements']:raise Refused('Invalid source replacements')
            for item in spec['replacements']:
                if (not isinstance(item,dict) or set(item)!={'before','after','count'}
                        or not isinstance(item['before'],str) or not item['before']
                        or not isinstance(item['after'],str) or type(item['count']) is not int
                        or item['count']<=0):raise Refused('Invalid source replacement')


def main():
    if sys.argv[1:] not in ([],['--check']):
        print('Invalid source delivery arguments',file=sys.stderr);return 1
    try:
        plan=(Path(__file__).parent/'prevention-replacements.json')
        if plan.stat().st_size>MAX_BYTES:raise Refused('Oversized source plan')
        specs=json.loads(plan.read_text())
        validate_plan(specs)
        # Prevalidate all targets before making any changes.
        for item in specs:deliver(item,check=True)
        changed=sum(deliver(item,check='--check' in sys.argv) for item in specs)
    except (Refused,OSError,ValueError,KeyError,TypeError,RecursionError):
        print('Source delivery refused; private review required',file=sys.stderr);return 1
    print('changed' if changed else 'unchanged');return 0

if __name__=='__main__':sys.exit(main())
