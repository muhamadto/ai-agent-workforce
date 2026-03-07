---
name: shortcut-to-vibe
description: Import Shortcut stories into VibeKanban. Fetch stories from a Shortcut epic or search query and create matching tasks in a VibeKanban project.
---

# Shortcut → VibeKanban Import Skill

Import Shortcut stories into VibeKanban using the `short` CLI and the VibeKanban REST API.

## Prerequisites

```bash
# Verify short CLI
which short || echo "short CLI not found — install via: brew install short"
short search -o me -l 1 2>/dev/null || echo "Not authenticated — run: short install"

# Verify VibeKanban is running — ask user for the URL (e.g. http://127.0.0.1:52526)
curl -s <VIBE_URL>/api/projects | python3 -m json.tool
```

## Step-by-Step Import

### 1. Get the VibeKanban URL

Ask the user for the VibeKanban URL if not provided. It looks like:
`http://127.0.0.1:<port>` (port changes each run — check the browser tab or terminal output).

### 2. List available projects

```bash
curl -s <VIBE_URL>/api/projects
```

Returns projects with `id` and `name`. Ask the user which project to import into if not specified.

### 3. Fetch stories from Shortcut

From a URL — extract the ID and fetch:
```bash
# https://app.shortcut.com/<org>/story/<ID>  →  short story <ID>
short story <ID>
```

From an epic:
```bash
short search -e <epic_id>
```

From a query or state:
```bash
short search "<query>"
short search -s "Ready for Development"
```

### 4. Map priority

| Shortcut priority | VibeKanban status |
|---|---|
| p1 / critical | urgent |
| p2 / high | high |
| p3 / medium | medium |
| p4 / low | low |
| none | omit |

### 5. Create the task in VibeKanban

```bash
curl -s -X POST <VIBE_URL>/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<story name>",
    "description": "[sc-<ID>] https://app.shortcut.com/<org>/story/<ID>\n\n<story description>",
    "project_id": "<project_id>"
  }'
```

Always include `[sc-<ID>]` and the Shortcut URL in the description for traceability.

### 6. Importing an epic (optional)

Create a parent task for the epic first, then create each story as a subtask using `parent_task_id`:

```bash
# Create parent
curl -s -X POST <VIBE_URL>/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "<epic name>", "project_id": "<project_id>"}'

# Create subtask
curl -s -X POST <VIBE_URL>/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "<story name>", "project_id": "<project_id>", "parent_task_id": "<epic_task_id>"}'
```

## Example Prompts

> "Import https://app.shortcut.com/sandpip3rs/story/14 into VibeKanban"

> "Import all stories from Shortcut epic 5 into the VibeKanban project 'mac-setup'"

## Deduplication

Before creating, check for existing tasks to avoid duplicates:

```bash
curl -s "<VIBE_URL>/api/tasks?project_id=<project_id>" | grep "sc-<ID>"
```

Skip if already present.

## Notes

- `short search` returns up to 25 results by default; use `-l <n>` for more
- Story type (feature/bug/chore) has no VibeKanban equivalent — include it in the description
- The VibeKanban port changes on each restart — always confirm the current URL with the user
