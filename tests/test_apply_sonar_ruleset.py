"""Exercise the reconciler with the GitHub process boundary replaced."""

import contextlib
import copy
import importlib.util
import io
import json
import pathlib
import subprocess
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/apply_sonar_ruleset.py"
DESIRED = {
    "name": "Sonar quality gate for main",
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [],
    "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
    "rules": [
        {
            "type": "required_status_checks",
            "parameters": {
                "required_status_checks": [
                    {"context": "SonarCloud Quality Gate", "integration_id": 15368}
                ],
                "strict_required_status_checks_policy": True,
                "do_not_enforce_on_create": False,
            },
        }
    ],
}


class FakeGitHub:
    """A stateful external API fake records changes to actual rulesets."""

    def __init__(self, rulesets=()):
        self.rulesets = {rule["id"]: copy.deepcopy(rule) for rule in rulesets}
        self.writes = []
        self.fail = False
        self.fail_write = False
        self.fail_readback = False
        self.corrupt_readback = False
        self.list_paths = []

    def run(self, command, **kwargs):
        assert command[:2] == ["gh", "api"]
        assert kwargs.get("shell", False) is False
        assert command[2].startswith("repos/muhamadto/ai-agent-workforce/rulesets")
        method = command[command.index("--method") + 1]
        endpoint = command[2]
        if (
            self.fail
            or (self.fail_write and method != "GET")
            or (self.fail_readback and self.writes and method == "GET")
        ):
            return subprocess.CompletedProcess(command, 1, "", "sensitive-api-response")
        if method == "GET" and "?" in endpoint:
            self.list_paths.append(endpoint)
            page = int(endpoint.split("page=")[-1])
            values = list(self.rulesets.values())[(page - 1) * 100 : page * 100]
            result = [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "source": r.get("source", "muhamadto/ai-agent-workforce"),
                    "source_type": r.get("source_type", "Repository"),
                }
                for r in values
            ]
        elif method == "GET":
            result = copy.deepcopy(self.rulesets[int(endpoint.rsplit("/", 1)[1])])
            if self.corrupt_readback and self.writes:
                result["enforcement"] = "disabled"
        elif method in ("POST", "PUT"):
            payload = json.loads(kwargs["input"])
            identifier = (
                max(self.rulesets, default=0) + 1
                if method == "POST"
                else int(endpoint.rsplit("/", 1)[1])
            )
            self.rulesets[identifier] = {**payload, "id": identifier}
            self.writes.append((method, identifier, payload))
            result = self.rulesets[identifier]
        else:
            raise AssertionError(f"Unexpected method {method}")
        return subprocess.CompletedProcess(command, 0, json.dumps(result), "")


class RulesetTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), "Ruleset reconciler is not implemented")
        spec = importlib.util.spec_from_file_location("apply_sonar_ruleset", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def run_script(self, fake, apply=False):
        output = io.StringIO()
        with patch.object(
            self.module.subprocess, "run", side_effect=fake.run
        ), contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = self.module.main(["--apply"] if apply else [])
        return status, output.getvalue()

    def test_preview_does_not_create_or_update_rules(self):
        fake = FakeGitHub()
        status, output = self.run_script(fake)
        self.assertEqual(status, 0)
        self.assertIn("create", output.lower())
        self.assertEqual(fake.rulesets, {})
        self.assertEqual(fake.writes, [])

    def test_preview_does_not_update_drifted_rule(self):
        existing = {**copy.deepcopy(DESIRED), "id": 9, "enforcement": "disabled"}
        fake = FakeGitHub([existing])
        status, output = self.run_script(fake)
        self.assertEqual(status, 0)
        self.assertIn("update", output.lower())
        self.assertEqual(fake.rulesets[9], existing)
        self.assertEqual(fake.writes, [])

    def test_apply_creates_only_the_committed_main_gate_and_is_idempotent(self):
        other = {
            "id": 1,
            "name": "Existing protection",
            "rules": [{"type": "deletion"}],
        }
        fake = FakeGitHub([other])
        self.assertEqual(self.run_script(fake, True)[0], 0)
        self.assertEqual(fake.rulesets[1], other)
        self.assertEqual(fake.writes[0][2], DESIRED)
        self.assertEqual(self.run_script(fake, True)[0], 0)
        self.assertEqual(len(fake.writes), 1)

    def test_apply_updates_only_its_existing_narrow_ruleset(self):
        existing = {**copy.deepcopy(DESIRED), "id": 9}
        existing["rules"][0]["parameters"][
            "strict_required_status_checks_policy"
        ] = False
        fake = FakeGitHub([existing])
        self.assertEqual(self.run_script(fake, True)[0], 0)
        self.assertEqual(fake.writes, [("PUT", 9, DESIRED)])

    def test_api_metadata_and_default_parameter_do_not_cause_writes(self):
        existing = {
            **copy.deepcopy(DESIRED),
            "id": 9,
            "created_at": "2026-01-01",
            "_links": {},
        }
        del existing["rules"][0]["parameters"]["do_not_enforce_on_create"]
        fake = FakeGitHub([existing])
        self.assertEqual(self.run_script(fake, True)[0], 0)
        self.assertEqual(fake.writes, [])

    def test_duplicate_name_is_refused_without_writes(self):
        fake = FakeGitHub([{**DESIRED, "id": 1}, {**DESIRED, "id": 2}])
        self.assertNotEqual(self.run_script(fake, True)[0], 0)
        self.assertEqual(fake.writes, [])

    def test_unexpected_rules_broader_scope_and_bypasses_are_refused(self):
        changes = [
            {"rules": [{"type": "deletion"}]},
            {"conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}}},
            {
                "bypass_actors": [
                    {"actor_id": 1, "actor_type": "Team", "bypass_mode": "always"}
                ]
            },
            {"target": "tag"},
        ]
        for change in changes:
            with self.subTest(change=change):
                fake = FakeGitHub([{**copy.deepcopy(DESIRED), **change, "id": 1}])
                self.assertNotEqual(self.run_script(fake, True)[0], 0)
                self.assertEqual(fake.writes, [])

    def test_api_failure_surfaces_without_sensitive_stderr(self):
        fake = FakeGitHub()
        fake.fail = True
        status, output = self.run_script(fake, True)
        self.assertNotEqual(status, 0)
        self.assertIn("GitHub API", output)
        self.assertNotIn("sensitive-api-response", output)

    def test_write_failure_is_nonzero_without_success_message(self):
        fake = FakeGitHub()
        fake.fail_write = True
        status, output = self.run_script(fake, True)
        self.assertNotEqual(status, 0)
        self.assertNotIn("applied and verified", output)
        self.assertNotIn("sensitive-api-response", output)
        self.assertEqual(fake.rulesets, {})

    def test_readback_failure_surfaces_partial_application(self):
        fake = FakeGitHub()
        fake.fail_readback = True
        status, output = self.run_script(fake, True)
        self.assertNotEqual(status, 0)
        self.assertNotIn("applied and verified", output)
        self.assertNotIn("sensitive-api-response", output)
        self.assertEqual(len(fake.writes), 1)

    def test_malformed_rules_fail_without_traceback_or_writes(self):
        for rule in (None, {"type": "required_status_checks", "parameters": None}):
            with self.subTest(rule=rule):
                fake = FakeGitHub(
                    [{**copy.deepcopy(DESIRED), "id": 1, "rules": [rule]}]
                )
                status, output = self.run_script(fake, True)
                self.assertNotEqual(status, 0)
                self.assertNotIn("Traceback", output)
                self.assertEqual(fake.writes, [])

    def test_parent_ruleset_with_same_name_is_not_owned(self):
        fake = FakeGitHub(
            [
                {
                    **copy.deepcopy(DESIRED),
                    "id": 1,
                    "source_type": "Organization",
                    "source": "muhamadto",
                }
            ]
        )
        self.assertNotEqual(self.run_script(fake, True)[0], 0)
        self.assertEqual(fake.writes, [])

    def test_readback_mismatch_fails_the_apply(self):
        fake = FakeGitHub()
        fake.corrupt_readback = True
        self.assertNotEqual(self.run_script(fake, True)[0], 0)

    def test_pagination_finds_existing_rule_on_second_page(self):
        others = [{"id": n, "name": f"Other {n}"} for n in range(1, 101)]
        fake = FakeGitHub([*others, {**DESIRED, "id": 101}])
        self.assertEqual(self.run_script(fake, True)[0], 0)
        self.assertEqual(fake.writes, [])
        self.assertEqual(len(fake.list_paths), 2)
        self.assertTrue(
            all("includes_parents=false" in path for path in fake.list_paths)
        )


if __name__ == "__main__":
    unittest.main()
