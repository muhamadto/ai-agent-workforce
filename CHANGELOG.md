# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Gemini CLI agents with repo-navigation-first design (9 specialized agents)
- Model selection guide to README with per-agent recommendations
- Build status and SonarCloud badges to README
- GitHub Actions workflow for Ansible linting and SonarCloud scanning
- CodeQL advanced security scanning workflow
- YAML linting configuration (150 char line limit)
- Git hooks for pre-commit and pre-push quality gates

### Changed
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
