# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `qe-engineer` agent for Claude, Qwen, and Gemini — test strategy, automation, BDD, performance, and CI/CD quality gates
- `business-analyst` agent for Claude, Qwen, and Gemini — requirements elicitation, user stories, acceptance criteria, domain modeling
- `/run-quality-checks` skill — detect build tool (Maven, Gradle, npm, Python) and run full pre-commit quality gate
- `/threat-model` skill — produce a STRIDE threat model for any feature or component
- `/api-design` skill — design and review REST/OpenAPI or gRPC contracts for correctness, security, and business alignment
- `/test-plan` skill — produce a structured test plan (unit/integration/E2E/performance/security) from a user story
- `/git-commit` skill — Conventional Commits compliant commit workflow with hook awareness (deployed in #11)
- `principal-engineer` agent now references `/api-design` skill for API design arbitration
- Gemini CLI agents with repo-navigation-first design (9 specialized agents)
- Model selection guide to README with per-agent recommendations
- Build status and SonarCloud badges to README
- GitHub Actions workflow for Ansible linting and SonarCloud scanning
- CodeQL advanced security scanning workflow
- YAML linting configuration (150 char line limit)
- Git hooks for pre-commit and pre-push quality gates

### Changed
- All agent `## Conventional Commits` sections collapsed to single-line reference to `/git-commit` skill
- Gemini agents: replaced inline `## Commit Format` blocks with `/git-commit` skill reference
- `secops-engineer` (Claude, Qwen): replaced inline STRIDE section with `/threat-model` skill reference
- `identity-security-developer` (all models): workflow threat modeling step now references `/threat-model` skill
- `business-analyst` (all models): API contract review now references `/api-design` skill
- Backend, frontend, mobile, data engineers: test coverage sections condensed; detailed methodology moved to `/test-plan` skill
- Backend, frontend, mobile, data engineers: pre-commit quality workflow now references `/run-quality-checks` skill
- Skills deployed to central `~/.skills/` and symlinked per installed model (`~/.claude/skills`, `~/.qwen/skills`, `~/.gemini/skills`)
- Migrated SonarCloud scan to non-deprecated `sonarqube-scan-action@v5`
- Renamed `vibe-kanban` role to `vibekanban` (ansible-lint compliance)
- Fixed codeql.yml YAML indentation and line length violations
- Updated build workflow for Ansible projects (Python instead of Node.js)
- Updated sonar-project.properties for Ansible YAML analysis

### Fixed
- Qwen settings.json: removed unsupported `subagents` and `hooks` settings
- macOS Seatbelt compatibility for ansible-lint in git hooks
- SonarCloud project configuration for Ansible codebase

### Removed
- Duplicate documentation files from Qwen role (consolidated at repo root)
- Inline commit convention documentation from all agent files (single source of truth: `/git-commit` skill)
- Node.js dependencies from build workflow (not applicable to Ansible)

## [0.2.0] - 2026-03-07

### Added
- Gemini CLI agents with playbook-style prompts (explore-first, tool-aware)
- 9 specialized Gemini agents matching Claude/Qwen coverage:
  - architecture-guardian: Dependency topology mapper, Clean Architecture enforcer
  - backend-developer: Java 24+, Spring Boot 4.x, repo-exploration first
  - data-engineer: ETL/ELT, dbt, Spark, data lineage expert
  - frontend-developer: React, Next.js, Flutter, component tree mapper
  - identity-security-developer: OAuth2, OIDC, zero-trust specialist
  - infrastructure-engineer: AWS, GCP, Kubernetes, IaC-first approach
  - mobile-engineer: iOS, Android, Flutter, platform pattern reader
  - principal-engineer: Problem mapper, task decomposer, ADR writer
  - secops-engineer: OWASP expert, security scanner, paranoid by design
- Gemini settings.json with MCP server configurations
- Model comparison table (Claude vs Qwen vs Gemini)
- Agent-to-model matching recommendations

### Changed
- Gemini agents use gemini-2.5-pro with role-specific attention cones
- Constraint checkpoints woven mid-workflow (not just declared upfront)
- architecture-guardian and principal-engineer granted shell access for investigation
- Exploration blocks tuned per role scope (not uniform copy-paste)

## [0.1.0] - 2026-03-07

### Added
- Initial release
- Claude and Qwen agent deployment
- VibeKanban integration
- Basic Ansible automation framework
