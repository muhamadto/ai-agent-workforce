# ADR-0001: Require the scanner's Sonar quality gate

**Date:** 2026-10-07  
**Status:** Accepted  
**Deciders:** Repository maintainer, architecture guardian, principal engineer

## Context

The required `build` check uploads Sonar analysis with
`sonar.qualitygate.wait=false`, so success does not establish that the quality
gate passed. GitHub requires no Sonar check. SonarCloud reports the project as
unbound to GitHub and therefore publishes no native PR check; it also retains
`master` as its main branch while the repository uses `main`.

## Decision

Run scanning in an independent GitHub Actions job named
`SonarCloud Quality Gate`. Enable scanner quality-gate waiting with a
300-second processing timeout and a 15-minute job timeout. Preserve analysis
scope and quality thresholds. Every PR into `main`, including drafts,
documentation changes and retargeted PRs, receives the check.

Require this check from GitHub Actions integration `15368` using a committed,
additive ruleset scoped to `refs/heads/main`, with an up-to-date branch and no
bypass actors. Activate the rule only after the implementation PR's current
head produces a passing gate. Preview and repeated application must not write
settings unnecessarily; unrelated protections remain intact.

## Alternatives

- **Native SonarCloud check:** useful PR decoration, but requires project binding
  and Sonar administration access before GitHub receives the check.
- **Wait inside `build`:** enforces gate completion but hides Sonar behind the
  general build check. The independent job provides a stable required check.

## Consequences

- Rejected gates, scan errors and processing timeouts block merging.
- Missing scan credentials fail the job. Fork and Dependabot PRs do not receive
  protected secrets; a maintainer must run changes through a trusted branch
  after reviewing them. There is no secret-bearing `pull_request_target` flow.
- Sonar availability becomes a merge dependency. Restore the service or fix
  the failing scan rather than weakening the rule.
- SonarCloud binding and main-branch alignment remain separate setup work,
  recorded locally with pending external tracking.

## Reference

[Sonar quality-gate analysis parameters](https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/analysis-parameters/parameters-not-settable-in-ui)
