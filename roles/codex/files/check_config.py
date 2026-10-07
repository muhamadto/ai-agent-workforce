import json
import sys
import tomllib
from pathlib import Path

from check_storage import read_regular_file


def proposed_config(content: str, block: str) -> tuple[str, str]:
    lines = content.splitlines(keepends=True)
    begin = "# BEGIN AI AGENT WORKFORCE\n"
    end = "# END AI AGENT WORKFORCE\n"
    starts = [index for index, line in enumerate(lines) if line == begin]
    ends = [index for index, line in enumerate(lines) if line == end]
    marker_lines = [line for line in lines if line.rstrip("\r\n") in (begin.rstrip(), end.rstrip())]
    if marker_lines and (len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]):
        raise ValueError("Codex registration block markers are malformed.")
    insertion = starts[0] if starts else len(lines)
    if starts:
        del lines[starts[0]:ends[0] + 1]
    unmanaged = "".join(lines)
    if insertion > 0 and not lines[insertion - 1].endswith("\n"):
        lines[insertion - 1] += "\n"
    if block:
        if not block.endswith("\n"):
            block += "\n"
        lines[insertion:insertion] = [begin, *block.splitlines(keepends=True), end]
    return unmanaged, "".join(lines)


def main() -> int:
    try:
        settings = json.load(sys.stdin)
        content = read_regular_file(Path(settings["path"]))
        unmanaged, proposed = proposed_config(content, settings["block"] if settings["state"] == "present" else "")
        tomllib.loads(content)
        config = tomllib.loads(unmanaged)
        tomllib.loads(proposed)
    except (OSError, ValueError):
        print("Existing or proposed Codex configuration is unsafe or invalid; repair it before changing workforce agents.", file=sys.stderr)
        return 1
    agents = config.get("agents", {})
    if not isinstance(agents, dict):
        print("Existing Codex agents configuration is not a table.", file=sys.stderr)
        return 1
    agent_files = settings.get("agent_files")
    if agent_files is None:
        agent_files = [path.name for path in (Path(__file__).parent / "agents").glob("*.toml")]
    names = {Path(filename).stem for filename in agent_files}
    if settings["state"] == "present" and names & agents.keys():
        print("A workforce agent is already registered outside the managed block; resolve the collision explicitly.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
