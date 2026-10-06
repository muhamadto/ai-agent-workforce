import re
import sys
import tomllib
from pathlib import Path


def main() -> int:
    content = sys.stdin.read()
    unmanaged = re.sub(
        r"(?m)^# BEGIN AI AGENT WORKFORCE\n.*?^# END AI AGENT WORKFORCE(?:\n|$)",
        "",
        content,
        flags=re.S,
    )
    try:
        tomllib.loads(content)
        config = tomllib.loads(unmanaged)
    except tomllib.TOMLDecodeError:
        print("Existing Codex config.toml is invalid; repair it before installing workforce agents.", file=sys.stderr)
        return 1
    agents = config.get("agents", {})
    if not isinstance(agents, dict):
        print("Existing Codex agents configuration is not a table.", file=sys.stderr)
        return 1
    names = {path.stem for path in (Path(__file__).parent / "agents").glob("*.toml")}
    if names & agents.keys():
        print("A workforce agent is already registered outside the managed block; resolve the collision explicitly.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
