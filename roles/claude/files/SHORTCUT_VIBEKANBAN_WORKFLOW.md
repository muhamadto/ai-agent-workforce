[//]: # (Licensed to Muhammad Hamadto 2026)
[//]: # (Licensed under the Apache License, Version 2.0)

# Shortcut → VibeKanban → Parallel AI Agents Workflow

This guide explains how to use Shortcut MCP and VibeKanban MCP to orchestrate parallel work between Claude Code and Qwen Code agents.

## Architecture Overview

```
Shortcut (Requirements)
    ↓ Shortcut MCP
Claude/Qwen AI Agents
    ↓ VibeKanban MCP
VibeKanban Task Board
    ↓ start_workspace_session
Parallel Agent Teams
    ├─ Claude Code (Agent Teams)
    └─ Qwen Code (SubAgents)
```

## Prerequisites

1. **MCP Servers Configured** (already set in settings.json):
   - Shortcut MCP
   - VibeKanban MCP

2. **API Token**:
   - Set `SHORTCUT_API_TOKEN` in your environment or settings

3. **VibeKanban Running**:
   ```bash
   npx vibe-kanban
   # Access at http://localhost:3000
   ```

## Available MCP Tools

### Shortcut MCP Tools
- `list_stories` - Fetch stories from Shortcut
- `get_story` - Get story details
- `create_story` - Create new stories
- `update_story` - Update story status/details
- `list_epics` - List epics
- `search_stories` - Search with filters

### VibeKanban MCP Tools
- `list_projects` - List all VibeKanban projects
- `create_task` - Create task from Shortcut story
- `list_tasks` - View tasks by project/status
- `update_task` - Update task progress
- `get_task` - Get task details
- `start_workspace_session` - Launch coding agent on task
- `delete_task` - Remove completed tasks

## Workflow Examples

### Example 1: Fetch Epic → Create Tasks

**Command to AI:**
```
Fetch all stories from Shortcut epic "User Authentication"
and create corresponding tasks in VibeKanban project "auth-service"
```

**What happens:**
1. AI uses Shortcut MCP `list_stories` with epic filter
2. For each story, AI uses VibeKanban MCP `create_task`
3. Tasks appear in VibeKanban UI

### Example 2: Start Parallel Work

**Command to AI:**
```
Start working on VibeKanban tasks for project "auth-service".
Use Claude team for architecture tasks and Qwen for implementation tasks.
```

**What happens:**
1. AI queries tasks via `list_tasks`
2. Creates Claude team with `TeamCreate`
3. Distributes tasks:
   - Claude agents: Complex reasoning (architecture, security)
   - Qwen subagents: Code generation (CRUD, tests)
4. Each agent works in isolated feature branches
5. Progress tracked in VibeKanban

### Example 3: Launch Specific Agent on Task

**Command to AI:**
```
Start working on task "Implement OAuth2 flow" using Claude Code
```

**What happens:**
1. AI uses `get_task` to find task ID
2. Calls `start_workspace_session(task_id, executor="claude-code")`
3. Claude Code agent starts in isolated workspace
4. Creates feature branch automatically
5. Implements and commits changes

### Example 4: Hybrid Coordination

**Command to AI:**
```
Analyze all "In Progress" tasks in VibeKanban project "api-service".
Assign complex refactoring to Claude team,
unit test generation to Qwen agents.
```

**What happens:**
1. Query tasks: `list_tasks(project_id, status="in_progress")`
2. AI analyzes task complexity
3. Routes work:
   - Complex → Claude Agent Teams
   - Repetitive → Qwen SubAgents
4. Both work in parallel
5. Results merged via VibeKanban PR management

## Task Routing Strategy

### Use Claude Code For:
- Architectural decisions
- Security reviews
- Complex multi-system refactoring
- Design patterns implementation
- Cross-cutting concerns

### Use Qwen Code For:
- CRUD implementations
- Unit test generation
- Boilerplate code
- Data model scaffolding
- API endpoint creation

### Use Both (Parallel):
- Full-stack features
- Large epics with multiple stories
- Independent modules
- Microservices development

## VibeKanban Executors

When calling `start_workspace_session`, use:
- `claude-code` or `CLAUDE_CODE`
- `qwen-code` or `QWEN_CODE`
- Also available: `amp`, `gemini`, `codex`, `opencode`, `cursor_agent`, `copilot`, `droid`

## Integration Patterns

### Pattern 1: Story-Driven Development
```
1. PM creates Shortcut epic/stories
2. AI fetches stories → VibeKanban tasks
3. Daily: "Start work on today's tasks"
4. AI distributes to Claude/Qwen teams
5. PRs auto-created per task
6. Review and merge via VibeKanban UI
```

### Pattern 2: Sprint Automation
```
1. Sprint planning in Shortcut
2. "Import sprint stories to VibeKanban"
3. "Assign all backend tasks to Qwen, frontend to Claude"
4. Agents work in parallel
5. Daily standups: "Status of all tasks?"
6. Burndown tracked in VibeKanban
```

### Pattern 3: Intelligent Task Routing
```
1. "Fetch unassigned Shortcut stories"
2. AI analyzes complexity, dependencies
3. Auto-routing:
   - High complexity → Claude
   - Low complexity → Qwen
   - Independent → Parallel
4. Progress synced back to Shortcut
```

## Commands for AI

### Setup Phase
```
"Initialize VibeKanban project 'my-service' and
sync all Shortcut stories from epic 'Q1 Goals'"
```

### Daily Work
```
"What tasks are ready to start in VibeKanban?"
"Start working on priority tasks using both Claude and Qwen"
```

### Status Checks
```
"Show me progress on all VibeKanban tasks"
"Which tasks are blocked?"
"Sync task status back to Shortcut"
```

### Coordination
```
"Create a Claude team for the frontend tasks"
"Assign all API tasks to Qwen subagents"
"Work on these 5 tasks in parallel"
```

## Environment Variables

Set these in your shell profile or `.envrc`:

```bash
# Shortcut API Token
export SHORTCUT_API_TOKEN="your-token-here"

# Optional: VibeKanban configuration
export VK_ALLOWED_ORIGINS="http://localhost:3000"
export MCP_HOST="localhost"
```

## Troubleshooting

### MCP Server Not Found
```bash
# Verify VibeKanban is running
curl http://localhost:3000

# Check MCP server accessibility
npx vibe-kanban@latest --mcp
```

### Shortcut API Issues
```bash
# Test token
curl -X GET \
  -H "Content-Type: application/json" \
  -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  https://api.app.shortcut.com/api/v3/member
```

### Agent Team Communication
- Claude teams use tmux split panes
- Qwen subagents report hierarchically
- Both can access same VibeKanban project
- Ensure no git conflicts via feature branches

## Best Practices

1. **One Task = One Feature Branch**
   - VibeKanban auto-creates branches
   - Keep changes isolated per task

2. **Clear Task Descriptions**
   - AI needs context to route work
   - Include acceptance criteria
   - Link to Shortcut story for details

3. **Status Synchronization**
   - Update VibeKanban task status
   - Optionally sync back to Shortcut
   - Keep stakeholders informed

4. **Agent Specialization**
   - Let Claude handle complexity
   - Let Qwen handle volume
   - Review before merging

5. **Git Hygiene**
   - Pre-commit hooks still run
   - Quality gates enforced
   - PRs auto-created by VibeKanban

## References

- [Shortcut API Documentation](https://shortcut.com/api)
- [VibeKanban MCP Server](https://www.vibekanban.com/docs/integrations/vibe-kanban-mcp-server)
- [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Qwen Code SubAgents](https://qwenlm.github.io/qwen-code-docs/en/users/features/sub-agents/)

## Next Steps

1. Deploy updated settings:
   ```bash
   ansible-playbook playbook.yml -e setup_state=present --limit local --tags ai
   ```

2. Set your Shortcut API token:
   ```bash
   echo 'export SHORTCUT_API_TOKEN="your-token"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. Start VibeKanban:
   ```bash
   npx vibe-kanban
   ```

4. Try the workflow:
   ```
   "List my Shortcut stories and create VibeKanban tasks"
   ```

Enjoy orchestrating your AI development team! 🚀
