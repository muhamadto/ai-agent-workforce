# Sonar quality gate enforcement

PRs into `main` run the independent **SonarCloud Quality Gate** check. The
scanner waits for the uploaded analysis's quality gate before reporting
success. Its processing timeout is 300 seconds; the entire job is limited to
15 minutes. Missing or invalid credentials, scanner errors, rejected gates and
timeouts fail the check. Draft and documentation-only PRs receive the same gate.

Analysis scope and quality thresholds are defined by the existing project
configuration. SonarCloud's GitHub binding is not needed for this Actions check.
The binding and the project's stale `master` main-branch setting are recorded
as separate setup work. See [ADR-0001](adr/0001-require-sonar-quality-gate.md).

## Required-check ruleset

The committed policy is `.github/rulesets/sonar-quality-gate.json`. It requires
the exact check name from GitHub Actions integration `15368`, an up-to-date
branch and no bypass actors, and applies only to `refs/heads/main`. Apply or
update it in the repository's GitHub rulesets settings (administration access
required); no administration credential is passed to CI. Before activating it,
confirm the current head of the implementation PR has a passing
`SonarCloud Quality Gate` check. Verify with:

```sh
gh api repos/muhamadto/ai-agent-workforce/rules/branches/main
gh pr checks --required
```

## Failed or missing checks

Inspect the gate job's logs and the associated Sonar analysis. Fix credentials,
analysis errors or code findings, then rerun the workflow or update the PR.
Service outages and processing timeouts block merging until resolved.

Fork and Dependabot PRs do not receive the repository's `SONAR_TOKEN`; they fail
the credential check. After reviewing the proposed changes, a maintainer can
analyse them from a trusted repository branch. Do not expose secrets to
untrusted code, switch to `pull_request_target`, or skip the required gate.

Changes to the policy must be reviewed and committed through a PR; maintainers
must not disable the gate as a troubleshooting shortcut.
