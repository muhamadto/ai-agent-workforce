#!/usr/bin/env python3
#
# Licensed to Muhammad Hamadto 2026
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
"""Fail the playbook if any agent frontmatter references an unresolvable skill.

A skill reference resolves if it is one of:
  - a local skill directory under roles/skills/files/<name>/
  - a GitHub-sourced skill selected in group_vars/all.yml (github_skill_sources)
  - a Claude Code built-in command (allowlist below)

Run from anywhere; paths are resolved relative to the repo root.
"""
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent

# Claude Code built-in slash commands that agents may list as skills.
BUILTINS = {"review"}


def frontmatter_skills(path: Path) -> list[str]:
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S)
    if not match:
        return []
    skills_block = re.search(r"^skills:\n((?:[ \t]+-[ \t]+\S+\n)+)", match.group(1), re.M)
    if not skills_block:
        return []
    return re.findall(r"-[ \t]+(\S+)", skills_block.group(1))


def github_selected_skills() -> set[str]:
    config = yaml.safe_load((REPO / "group_vars" / "all.yml").read_text()) or {}
    selected: set[str] = set()
    for source in config.get("github_skill_sources") or []:
        if source.get("enabled", True):
            selected.update(source.get("selected_skills") or [])
    return selected


def main() -> int:
    local = {p.name for p in (REPO / "roles" / "skills" / "files").iterdir() if p.is_dir()}
    github = github_selected_skills()
    allowed = local | github | BUILTINS

    errors = []
    for role in ("claude", "litellm"):
        for agent in sorted((REPO / "roles" / role / "files" / "agents").glob("*.md")):
            for skill in frontmatter_skills(agent):
                if skill not in allowed:
                    errors.append(
                        f"roles/{role}/files/agents/{agent.name}: skill '{skill}' has no "
                        "matching directory in roles/skills/files/, no github_skill_sources "
                        "selection, and is not a known builtin"
                    )

    if errors:
        print("Unresolved agent skill references:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(
        f"All agent skill references resolve across roles/claude and roles/litellm "
        f"({len(local)} local, {len(github)} github-sourced, {len(BUILTINS)} builtin)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
