#!/usr/bin/env python3
"""Preview or reconcile the dedicated Sonar ruleset through the authenticated gh CLI.

Default invocation is read-only. Use --apply only after the implementation PR's
current head has published a passing SonarCloud Quality Gate. This prerequisite
is verified by the operator before activation, not inferred from older PR runs.
Existing branch protection and unrelated rulesets are never written.
"""

import argparse
import copy
import json
import pathlib
import subprocess
import sys

REPOSITORY = "muhamadto/ai-agent-workforce"
ENDPOINT = f"repos/{REPOSITORY}/rulesets"
DEFINITION = (
    pathlib.Path(__file__).resolve().parents[1]
    / ".github/rulesets/sonar-quality-gate.json"
)
NAME = "Sonar quality gate for main"
CONDITIONS = {"ref_name": {"include": ["refs/heads/main"], "exclude": []}}
CHECKS = [{"context": "SonarCloud Quality Gate", "integration_id": 15368}]
WRITABLE = ("name", "target", "enforcement", "bypass_actors", "conditions", "rules")


class ReconcileError(Exception):
    """A surfaced configuration or API failure; messages contain no API payloads."""


def api(endpoint, method="GET", payload=None):
    command = [
        "gh",
        "api",
        endpoint,
        "--method",
        method,
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28",
    ]
    if payload is not None:
        command.extend(["--input", "-"])
    try:
        result = subprocess.run(
            command,
            input=json.dumps(payload) if payload is not None else None,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ReconcileError("GitHub API command could not complete.") from error
    if result.returncode:
        raise ReconcileError(
            f"GitHub API {method} failed (gh exit {result.returncode}); check authentication and repository administration access."
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ReconcileError("GitHub API returned invalid JSON.") from error


def validate_owned(rule):
    """Refuse same-name collisions before changing an existing protection."""
    if not isinstance(rule, dict):
        raise ReconcileError("Invalid ruleset definition.")
    if (
        rule.get("name") != NAME
        or rule.get("target") != "branch"
        or rule.get("conditions") != CONDITIONS
        or rule.get("bypass_actors") != []
        or rule.get("enforcement") not in ("active", "evaluate", "disabled")
    ):
        raise ReconcileError(
            "Refusing a ruleset with unexpected ownership, scope or bypass actors."
        )
    rules = rule.get("rules")
    if not isinstance(rules, list) or len(rules) != 1:
        raise ReconcileError("Refusing a ruleset containing unrelated rules.")
    check = rules[0]
    if not isinstance(check, dict) or not isinstance(check.get("parameters"), dict):
        raise ReconcileError(
            "Refusing invalid status-check requirements or parameters."
        )
    parameters = check["parameters"]
    if (
        check.get("type") != "required_status_checks"
        or parameters.get("required_status_checks") != CHECKS
        or set(parameters)
        - {
            "required_status_checks",
            "strict_required_status_checks_policy",
            "do_not_enforce_on_create",
        }
        or not isinstance(parameters.get("strict_required_status_checks_policy"), bool)
        or not isinstance(parameters.get("do_not_enforce_on_create", False), bool)
    ):
        raise ReconcileError(
            "Refusing unexpected status-check requirements or parameters."
        )


def writable(rule):
    """Exclude response metadata and normalise GitHub's omitted false default."""
    result = {key: copy.deepcopy(rule[key]) for key in WRITABLE}
    result["rules"][0]["parameters"].setdefault("do_not_enforce_on_create", False)
    return result


def find_existing():
    matches = []
    page = 1
    while True:
        listing = api(f"{ENDPOINT}?includes_parents=false&per_page=100&page={page}")
        if not isinstance(listing, list):
            raise ReconcileError("GitHub API returned an invalid ruleset listing.")
        for entry in listing:
            if not isinstance(entry, dict):
                raise ReconcileError("GitHub API returned an invalid ruleset entry.")
            if entry.get("name") == NAME:
                if (
                    entry.get("source_type") != "Repository"
                    or entry.get("source") != REPOSITORY
                ):
                    raise ReconcileError("Refusing a ruleset owned by another source.")
                identifier = entry.get("id")
                if type(identifier) is not int or identifier <= 0:
                    raise ReconcileError("GitHub API returned an invalid ruleset ID.")
                matches.append(identifier)
        if len(listing) < 100:
            break
        page += 1
    if len(matches) > 1:
        raise ReconcileError(
            "Duplicate managed ruleset names; refusing ambiguous ownership."
        )
    if not matches:
        return None, None
    existing = api(f"{ENDPOINT}/{matches[0]}")
    validate_owned(existing)
    return matches[0], existing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply after verifying a passing gate on the implementation PR's current head.",
    )
    args = parser.parse_args(argv)
    try:
        desired = json.loads(DEFINITION.read_text())
        validate_owned(desired)
        if (
            set(desired) != set(WRITABLE)
            or desired["enforcement"] != "active"
            or desired["rules"][0]["parameters"]["strict_required_status_checks_policy"]
            is not True
            or desired["rules"][0]["parameters"].get("do_not_enforce_on_create", False)
            is not False
        ):
            raise ReconcileError(
                "Committed ruleset must enforce the strict gate without extra fields."
            )
        desired = writable(desired)
        identifier, existing = find_existing()
        if existing is not None and writable(existing) == desired:
            print("Sonar ruleset already matches; no writes required.")
            return 0
        operation = "create" if identifier is None else "update"
        if not args.apply:
            print(
                f"Preview: would {operation} the Sonar ruleset for {REPOSITORY}. No writes performed."
            )
            print(json.dumps(desired, indent=2))
            return 0
        response = api(
            ENDPOINT if identifier is None else f"{ENDPOINT}/{identifier}",
            "POST" if identifier is None else "PUT",
            desired,
        )
        identifier = response.get("id") if isinstance(response, dict) else None
        if type(identifier) is not int or identifier <= 0:
            raise ReconcileError(
                "GitHub API write returned an invalid ruleset ID; inspect repository rulesets before retrying."
            )
        actual = api(f"{ENDPOINT}/{identifier}")
        validate_owned(actual)
        if writable(actual) != desired:
            raise ReconcileError(
                "Ruleset readback does not match; enforcement was not verified."
            )
        print(f"Sonar ruleset {identifier} applied and verified.")
        return 0
    except (ReconcileError, OSError, ValueError, KeyError, TypeError) as error:
        # Payloads and subprocess stderr can contain sensitive data; never print them.
        message = (
            str(error)
            if isinstance(error, ReconcileError)
            else "Invalid local definition or GitHub API response."
        )
        print(f"Error: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
