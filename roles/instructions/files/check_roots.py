import json
import sys
import unicodedata
from pathlib import Path


def main() -> int:
    try:
        settings = json.load(sys.stdin)
        roots = {name: Path(value) for name, value in settings.items()}
        if any(not root.is_absolute() or ".." in root.parts for root in roots.values()):
            raise ValueError("Managed storage requires absolute paths without traversal.")
        resolved = {name: root.resolve() for name, root in roots.items()}
        folded = {name: Path(unicodedata.normalize("NFC", str(root)).casefold())
                  for name, root in resolved.items()}
        for candidates in (roots, resolved, folded):
            for name, root in candidates.items():
                for other_name, other_root in candidates.items():
                    if name != other_name and (root == other_root or root in other_root.parents):
                        raise ValueError("Managed roles and shared storage must not overlap.")
        return 0
    except (OSError, RuntimeError, ValueError):
        print("Unsafe managed storage overlap; no changes made.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
