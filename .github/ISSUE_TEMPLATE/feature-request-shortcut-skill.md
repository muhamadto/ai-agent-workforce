---
name: Feature Request
description: Suggest a new feature or improvement
title: "[Feature]: "
labels: ["enhancement"]
assignees: []
---

## Feature Description

Add a native Shortcut story import skill to enable AI agents to fetch, create, and sync Shortcut stories directly without relying on third-party skills.

## Problem Statement

Currently, there are third-party Shortcut CLI skills available (e.g., `hefgi/shortcut-cli-skill`), but they present significant concerns:

### Security Risks of Third-Party Skills
- 🔴 **Single maintainer** - Individual developer, not an organization
- 🔴 **Minimal maintenance** - Only 1 commit, no releases published
- 🔴 **No security audits** - Code hasn't been reviewed for vulnerabilities
- 🔴 **Full API access** - Requires Shortcut API token with full workspace access
- 🔴 **Supply chain risk** - Could exfiltrate data or inject malicious code
- 🟡 **No version pinning** - Cannot lock to a specific secure version

### Current State

This repository already has foundational Shortcut integration:
- ✅ `roles/vibekanban/files/shortcut-vibe-sync.sh` - Direct API integration
- ✅ VibeKanban MCP server for task synchronization
- ✅ Shortcut MCP server configuration in agent settings

However, the integration is incomplete and lacks:
1. Direct AI agent access to Shortcut operations
2. Story import workflow from Shortcut → VibeKanban
3. Bi-directional sync (status updates back to Shortcut)
4. Comprehensive CLI tool for common operations

## Proposed Solution

### Option 1: Native Shortcut Skill (Recommended) ⭐

Create an official `shortcut` skill within this repository that:

**Features:**
- [ ] `short story <id>` - View story details
- [ ] `short search <filters>` - Search stories by owner, state, label, epic
- [ ] `short import <epic-id>` - Import all stories from an epic to VibeKanban
- [ ] `short sync` - Bi-directional sync between Shortcut and VibeKanban
- [ ] `short create <title>` - Create new Shortcut story
- [ ] `short update <id> <field>` - Update story state, title, description
- [ ] `short epic list` - List all epics
- [ ] `short epic stories <id>` - List stories in an epic

**Implementation:**
```bash
# Project structure
roles/shortcut/
├── files/
│   ├── shortcut-cli.sh          # Main CLI tool
│   ├── import-stories.sh        # Epic import workflow
│   └── sync-status.sh           # Bi-directional sync
├── tasks/
│   └── main.yml                 # Ansible deployment
└── README.md                    # Usage documentation

# Agent integration
~/.claude/agents/shortcut-manager.md
~/.qwen/agents/shortcut-manager.md
~/.gemini/agents/shortcut-manager.md
```

**Security Benefits:**
- ✅ Full code audit by repository maintainers
- ✅ Version pinned via Git tags
- ✅ No external dependencies beyond official Shortcut API
- ✅ Transparent authentication flow
- ✅ Regular security reviews as part of repo maintenance

### Option 2: Fork and Audit Third-Party Skill

If building from scratch is too time-intensive:

1. Fork `hefgi/shortcut-cli-skill` to `muhamadto/shortcut-cli-skill`
2. Conduct full security audit
3. Add security tests and CI checks
4. Pin to specific commit hash
5. Document audit findings

**Risks:** Still inherits upstream dependencies, maintenance burden.

### Option 3: Use Official Shortcut MCP Server

Check if Shortcut offers an official MCP server. If available:
- Lower maintenance burden
- Official support
- Better long-term sustainability

**Status:** As of 2026-03-07, no official Shortcut MCP server exists.

## Implementation Plan

### Phase 1: Core CLI Tool (Week 1)
- [ ] Create `shortcut-cli.sh` with basic operations
- [ ] Implement authentication (env var + interactive setup)
- [ ] Add story fetch, search, create, update operations
- [ ] Add epic list and stories operations
- [ ] Write unit tests for API calls

### Phase 2: VibeKanban Integration (Week 2)
- [ ] Create `import-stories.sh` workflow
- [ ] Map Shortcut states → VibeKanban statuses
- [ ] Sync story metadata (title, description, comments)
- [ ] Handle attachments and branches
- [ ] Add conflict resolution (which system is source of truth)

### Phase 3: AI Agent Integration (Week 3)
- [ ] Create `shortcut-manager` agent for all three models
- [ ] Document agent prompts and capabilities
- [ ] Add MCP server configuration
- [ ] Test with Claude, Qwen, and Gemini
- [ ] Create usage examples and workflows

### Phase 4: Bi-Directional Sync (Week 4)
- [ ] Track VibeKanban → Shortcut state changes
- [ ] Sync completion status back to Shortcut
- [ ] Handle offline scenarios (queue changes)
- [ ] Add sync conflict detection and resolution
- [ ] Create sync status dashboard

### Phase 5: Documentation & Testing (Week 5)
- [ ] Write comprehensive README
- [ ] Create video demo of workflow
- [ ] Add troubleshooting guide
- [ ] Security audit and penetration testing
- [ ] Performance testing with large workspaces

## Acceptance Criteria

- [ ] CLI tool passes all security reviews
- [ ] Can import 100+ stories from an epic without errors
- [ ] Bi-directional sync works reliably (≥99% success rate)
- [ ] All three AI models (Claude, Qwen, Gemini) can use the skill
- [ ] Documentation includes 5+ real-world workflow examples
- [ ] Zero third-party dependencies beyond official Shortcut API
- [ ] Ansible role deploys successfully to macOS and Linux

## Alternative Solutions Considered

| Solution | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **Use existing third-party skill** | Quick to implement | Security risks, no control | ❌ Not recommended |
| **Fork and audit third-party** | Faster than building from scratch | Still inherits risks, maintenance burden | 🟡 Acceptable fallback |
| **Build native skill** | Full control, auditable, secure | More development time | ✅ **Recommended** |
| **Wait for official MCP** | Official support, lower maintenance | May never exist, timeline unknown | 🟡 Monitor but don't block |
| **Use existing shortcut-vibe-sync.sh** | Already in repo, auditable | Limited features, not AI-integrated | 🟡 Enhance rather than replace |

## Additional Context

### Existing Integration
The repository already has `shortcut-vibe-sync.sh` which demonstrates:
- Shortcut API authentication
- Epic and story fetching
- VibeKanban task creation
- AI workflow examples

This feature request builds upon that foundation to create a production-ready, secure integration.

### Related Issues
- #XX - VibeKanban MCP server integration
- #XX - AI agent task routing improvements

### References
- [Shortcut API Documentation](https://developer.shortcut.com/api/rest/v3)
- [Official shortcut-cli](https://github.com/shortcut/shortcut-cli)
- [VibeKanban Documentation](https://www.vibekanban.com/docs/)
- [MCP Server Specification](https://modelcontextprotocol.io/)

---

**Priority:** High - Required for production AI agent workflows

**Estimated Effort:** 3-5 weeks

**Assignees:** @muhamadto @ericmm

**Labels:** `enhancement`, `security`, `shortcut-integration`, `ai-agents`
