"""Check the workflow contracts that make PR analysis fail closed."""

import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


class SonarGateTests(unittest.TestCase):
    def setUp(self):
        self.workflow = yaml.load(
            (ROOT / ".github/workflows/build.yml").read_text(), Loader=yaml.BaseLoader
        )

    def test_all_main_pr_updates_schedule_the_gate(self):
        trigger = self.workflow["on"]["pull_request"]
        self.assertEqual(trigger["branches"], ["main"])
        self.assertTrue(
            {"opened", "synchronize", "reopened", "edited"}.issubset(trigger["types"])
        )
        self.assertNotIn("paths", trigger)
        self.assertNotIn("paths-ignore", trigger)

    def test_gate_runs_independently_and_has_a_bounded_runtime(self):
        gate = self.workflow["jobs"].get("sonar-quality-gate", {})
        self.assertEqual(gate.get("name"), "SonarCloud Quality Gate")
        self.assertEqual(gate["timeout-minutes"], "15")
        for forbidden in ("if", "needs", "continue-on-error"):
            self.assertNotIn(forbidden, gate)
        for step in gate["steps"]:
            self.assertNotIn("if", step)
            self.assertNotIn("continue-on-error", step)

    def test_scan_waits_for_the_quality_gate(self):
        properties = dict(
            line.split("=", 1)
            for line in (ROOT / "sonar-project.properties").read_text().splitlines()
            if line.startswith("sonar.qualitygate.")
        )
        self.assertEqual(properties.get("sonar.qualitygate.wait"), "true")
        self.assertEqual(properties.get("sonar.qualitygate.timeout"), "300")

    def test_credentials_are_read_only_and_actions_are_pinned(self):
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        gate = self.workflow["jobs"].get("sonar-quality-gate", {})
        steps = gate.get("steps", [])
        checkout = next(
            (step for step in steps if "checkout@" in step.get("uses", "")), {}
        )
        self.assertEqual(
            checkout.get("uses"),
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        )
        self.assertEqual(checkout["with"]["fetch-depth"], "0")
        self.assertEqual(checkout["with"]["persist-credentials"], "false")
        scan = next(
            (step for step in steps if "scan-action@" in step.get("uses", "")), {}
        )
        self.assertEqual(
            scan.get("uses"),
            "SonarSource/sonarqube-scan-action@d209202bc7d53ff1cc128f7f907dac145c9d6ae9",
        )
        self.assertEqual(scan["env"]["SONAR_TOKEN"], "${{ secrets.SONAR_TOKEN }}")
        self.assertFalse(
            any(
                "scan-action@" in step.get("uses", "")
                for step in self.workflow["jobs"]["build"]["steps"]
            )
        )

    def test_missing_token_fails_before_scanning_without_disclosure(self):
        import os
        import subprocess

        steps = self.workflow["jobs"].get("sonar-quality-gate", {}).get("steps", [])
        check = next(
            (step for step in steps if step.get("name") == "Require Sonar credentials"),
            {},
        )
        self.assertTrue(check.get("run"), "Missing explicit credential check")
        for token, expected in (("", 1), ("synthetic-test-credential", 0)):
            result = subprocess.run(
                ["bash", "-e", "-c", check["run"]],
                env={**os.environ, "SONAR_TOKEN": token},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, expected)
            self.assertNotIn("synthetic-test-credential", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
