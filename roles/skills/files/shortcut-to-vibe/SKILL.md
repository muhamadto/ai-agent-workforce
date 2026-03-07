---
name: shortcut-to-vibe
description: Import Shortcut stories into VibeKanban. Fetch stories from a Shortcut epic or search query and create matching issues in a VibeKanban project.
---

# Shortcut → VibeKanban Import Skill

Import Shortcut stories into VibeKanban as issues using the `short` CLI and the `vibe_kanban` MCP server.

## Prerequisites

```bash
which short || echo "short CLI not found — install via: brew install short"
short search -o me -l 1 2>/dev/null || echo "Not authenticated — run: short install"
```

VibeKanban must be running and its MCP server active.

## Step-by-Step Import

### 1. Fetch stories from Shortcut

By epic ID:
```bash
short search -e <epic_id> --json
```

By search query:
```bash
short search "<query>" --json
```

By workflow state:
```bash
short search -s "Ready for Development" --json
```

Each story has: `id`, `name`, `description`, `story_type`, `estimate`, `labels`, and `priority`.

### 2. Discover the target VibeKanban project

Call `vibe_kanban.list_projects` to get available projects and their IDs.
Ask the user which project to import into if not already specified.

### 3. Map priority

| Shortcut priority | VibeKanban priority |
|---|---|
| p1 / critical | urgent |
| p2 / high | high |
| p3 / medium | medium |
| p4 / low | low |
| none / unset | omit |

### 4. Create issues in VibeKanban

For each story, call `vibe_kanban.create_issue` with:

```
title       = story name
description = story description (include Shortcut story ID and URL for traceability)
project_id  = selected project ID
priority    = mapped priority (omit if none)
```

Include the Shortcut story link in the description so the issue stays traceable:

```
[sc-<ID>] https://app.shortcut.com/<org>/story/<ID>

<original description>
```

### 5. Importing an epic as a parent issue (optional)

If importing a full epic, first create a parent issue for the epic itself:

```
vibe_kanban.create_issue(title=<epic name>, description=<epic description>, project_id=...)
```

Then create each story as a sub-issue using `parent_issue_id`:

```
vibe_kanban.create_issue(title=..., parent_issue_id=<epic issue id>, ...)
```

## Example Prompt

> "Import all stories from Shortcut epic 123 into the VibeKanban project 'backend-service'"

You will:
1. Run `short search -e 123 --json`
2. Call `vibe_kanban.list_projects`, confirm target project
3. Call `vibe_kanban.create_issue` for each story

## Notes

- Deduplication: before creating, optionally call `vibe_kanban.list_issues` to skip stories already imported (match by `[sc-<ID>]` in description)
- `short search` returns up to 25 results by default; use `-l <n>` for more
- Story type (feature/bug/chore) has no direct VibeKanban equivalent — include it in the description
