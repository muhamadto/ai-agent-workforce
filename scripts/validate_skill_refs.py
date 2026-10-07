#!/usr/bin/env python3
#
# Licensed to Muhammad Hamadto 2026
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
"""Validate agents, skill references and synchronised global operating rules.

A skill reference resolves if it is one of:
  - a local skill directory under roles/skills/files/<name>/
  - a GitHub-sourced skill selected in group_vars/all.yml (github_skill_sources)
  - a Claude Code built-in command (allowlist below)

Run from anywhere; paths are resolved relative to the repo root.
"""
import re
import sys
import tomllib
from pathlib import Path

import yaml

from dispatch_agent import DispatchError, routing

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


def codex_skills(path: Path) -> list[str]:
    agent = tomllib.loads(path.read_text())
    for field in ("name", "description", "developer_instructions"):
        if not isinstance(agent.get(field), str) or not agent[field].strip():
            raise ValueError(f"'{field}' must be a non-empty string")
    if agent["name"] != path.stem:
        raise ValueError("agent name must match its filename")
    return sorted(set(re.findall(
        r"~/.agents/skills/ai-agent-workforce/([a-z0-9-]+)/SKILL\.md",
        agent["developer_instructions"],
    )))


def global_rules_errors() -> list[str]:
    path = REPO / "instructions" / "AGENTS.md"
    if not path.is_file():
        return ["instructions/AGENTS.md: missing canonical global operating rules"]
    required = ("Communication, Language and Tone", "Workflow", "Specialist Delegation", "Skills and Safety")
    contents = path.read_text()
    return [f"instructions/AGENTS.md: missing '{heading}' section" for heading in required
            if not re.search(rf"^## {re.escape(heading)}(?: —[^\n]*)?\s*$", contents, re.M)]


def claude_skill_errors(allowed: set[str]) -> list[str]:
    errors = []
    for role in ("claude",):
        for agent in sorted((REPO / "roles" / role / "files" / "agents").glob("*.md")):
            for skill in frontmatter_skills(agent):
                if skill not in allowed:
                    errors.append(
                        f"roles/{role}/files/agents/{agent.name}: skill '{skill}' has no "
                        "matching directory in roles/skills/files/, no github_skill_sources "
                        "selection, and is not a known builtin"
                    )
    return errors


def specialist_routing_errors(codex_agents: list[Path]) -> list[str]:
    errors = []
    claude_names = {path.stem for path in (REPO / "roles" / "claude" / "files" / "agents").glob("*.md")}
    opencode_names = {path.stem for path in (REPO / "roles" / "opencode" / "files" / "agents").glob("*.md")}
    if {path.stem for path in codex_agents} != claude_names or opencode_names != claude_names:
        errors.append("Specialist agent names must match across Claude, OpenCode and Codex.")
    try:
        routes = routing(REPO / "config" / "agent-routing.toml")
        if set(routes) != claude_names:
            errors.append("Dispatcher routing must contain exactly the shared specialist names.")
    except DispatchError as error:
        errors.append(f"config/agent-routing.toml: {error}")
    return errors


def codex_skill_errors(codex_agents: list[Path], allowed: set[str]) -> list[str]:
    errors = []
    for agent in codex_agents:
        try:
            skills = codex_skills(agent)
        except ValueError as error:
            errors.append(f"{agent.relative_to(REPO)}: {error}")
            continue
        for skill in skills:
            if skill not in allowed:
                errors.append(f"{agent.relative_to(REPO)}: skill '{skill}' has no local or GitHub-sourced definition")
    return errors


def main() -> int:
    local = {path.name for path in (REPO / "roles" / "skills" / "files").iterdir() if path.is_dir()}
    github = github_selected_skills()
    codex_agents = sorted((REPO / "roles" / "codex" / "files" / "agents").glob("*.toml"))
    errors = global_rules_errors()
    errors.extend(claude_skill_errors(local | github | BUILTINS))
    errors.extend(specialist_routing_errors(codex_agents))
    errors.extend(codex_skill_errors(codex_agents, local | github))

    if errors:
        print("Invalid agents, unresolved skills or unsynchronised rules:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(
        f"All agent skill references resolve across roles/claude and {len(codex_agents)} Codex agents "
        f"({len(local)} local, {len(github)} github-sourced, {len(BUILTINS)} Claude builtin)."
    )
    print("Canonical global operating rules validated for Claude, OpenCode and Codex.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
