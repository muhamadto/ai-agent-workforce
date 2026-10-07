import json
import os
import stat
import sys
from pathlib import Path


def check_regular_file(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise ValueError("Codex storage requires regular single-link files.")
    return True


def read_regular_file(path: Path) -> str:
    if not check_regular_file(path):
        return ""
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, encoding="utf-8", newline="") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError("Codex storage requires regular single-link files.")
        return stream.read()


def main() -> int:
    try:
        settings = json.load(sys.stdin)
        home = Path(settings["home"])
        codex_home = Path(settings["codex_home"])
        managed = Path(settings["managed_dir"])
        protected_roots = (home, codex_home, codex_home / "agents", home / ".agents", home / ".agents/skills")
        if any(managed == root or managed in root.parents for root in protected_roots):
            raise ValueError("Codex managed storage must not contain native or user storage roots.")
        directories = {home, codex_home, codex_home / "agents", managed,
                       managed / "agents", home / ".agents", home / ".agents/skills"}
        for directory in list(directories):
            if not directory.is_absolute() or ".." in directory.parts:
                raise ValueError("Codex storage requires absolute directory paths.")
            directories.update(directory.parents)
        for directory in sorted(directories, key=lambda path: len(path.parts)):
            try:
                metadata = directory.lstat()
            except FileNotFoundError:
                continue
            if not stat.S_ISDIR(metadata.st_mode):
                raise ValueError("Codex storage requires real directories, not redirects.")
        marker = managed / ".managed"
        marker_exists = check_regular_file(marker)
        marker_content = read_regular_file(marker) if marker_exists else ""
        owned = marker_content in ("ai-agent-workforce:codex", "ai-agent-workforce:codex\n") or (
            marker_content in ("ai-agent-workforce\n", "ai-agent-workforce")
            and managed == home / ".codex/ai-agent-workforce"
        )
        if marker_exists and not owned:
            raise ValueError("Codex ownership marker is malformed.")
        check_regular_file(codex_home / "config.toml")
        for filename in settings["agent_files"]:
            check_regular_file(managed / "agents" / filename)
        print(json.dumps({"owned": owned}))
        return 0
    except (OSError, ValueError):
        print("Unsafe Codex storage or ownership marker; no changes made.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
