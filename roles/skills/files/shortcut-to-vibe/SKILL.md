---
name: shortcut-to-vibe
description: Import Shortcut stories into VibeKanban. Supports importing all stories, stories assigned to me, or a specific story/epic with all its children.
---

# Shortcut → VibeKanban Import Skill

Import Shortcut stories into VibeKanban using the `short` CLI and the VibeKanban REST API.

## Prerequisites

```bash
which short || echo "short CLI not found — install via: brew install short"
short search -o me -l 1 2>/dev/null || echo "Not authenticated — run: short install"
```

VibeKanban must be running. Ask the user for the URL (e.g. `http://127.0.0.1:54271`) — the port changes on each restart.

## Import Modes

### Mode 1: All stories

```bash
short search -l 100
```

Use `-l <n>` to control the limit. Shortcut defaults to 25.

### Mode 2: My stories

```bash
short search -o me
```

### Mode 3: Single story by ID or URL

Extract the ID from the URL if given (`https://app.shortcut.com/<org>/story/<ID>`):

```bash
short story <ID>
```

### Mode 4: Epic by ID or URL — imports epic + all child stories

Extract the ID from the URL if given (`https://app.shortcut.com/<org>/epic/<ID>`):

```bash
# 1. Fetch the epic itself
short epic <ID>

# 2. Fetch all stories in the epic
short search -e <ID> -l 100
```

Create the epic as a parent issue in VibeKanban, then create each story as a
child using `parent_issue_id` (see Step 5 below).

## Step-by-Step Import

### 1. Discover the target VibeKanban project

List remote projects:

```bash
curl -s "http://127.0.0.1:<port>/api/remote/projects?organization_id=<org_id>"
```

To get the org ID:

```bash
curl -s "http://127.0.0.1:<port>/api/projects"   # returns local projects — org_id is embedded
# or ask the user — they can find it in VibeKanban Settings > Organization Settings
```

Ask the user which project to import into if not already specified.
Note the `project_id` for the next steps.

### 2. Get the "To do" status ID

```bash
curl -s "http://127.0.0.1:<port>/api/remote/project-statuses?project_id=<project_id>"
```

Use the `id` of the status named `"To do"` as `status_id` in the create call.

### 3. Map Shortcut priority to VibeKanban priority

| Shortcut priority | VibeKanban priority |
|---|---|
| p1 / critical | urgent |
| p2 / high | high |
| p3 / medium | medium |
| p4 / low | low |
| none | null |

### 4. Check for duplicates (optional)

```bash
curl -s "http://127.0.0.1:<port>/api/remote/issues?project_id=<project_id>" | grep "sc-<ID>"
```

Skip stories already present (matched by `[sc-<ID>]` in description).

### 5. Create each issue

```bash
curl -s -X POST "http://127.0.0.1:<port>/api/remote/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<story name>",
    "description": "[sc-<ID>] https://app.shortcut.com/<org>/story/<ID>\n\n<story description>",
    "project_id": "<project_id>",
    "status_id": "<to_do_status_id>",
    "sort_order": <index>,
    "extension_metadata": null
  }'
```

- `sort_order`: use the story's position (0, 1, 2, …) to preserve ordering
- Always include `[sc-<ID>]` and the Shortcut URL for traceability
- Include story type (feature/bug/chore) in the description — VibeKanban has no equivalent field

### 6. For epic imports: link child stories

First create the epic as a parent issue (Step 5), capture its returned `id`.
Then create each story with `parent_issue_id` set:

```bash
curl -s -X POST "http://127.0.0.1:<port>/api/remote/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<story name>",
    "description": "[sc-<ID>] https://app.shortcut.com/<org>/story/<ID>\n\n<story description>",
    "project_id": "<project_id>",
    "status_id": "<to_do_status_id>",
    "sort_order": <index>,
    "parent_issue_id": "<epic_issue_id>",
    "extension_metadata": null
  }'
```

## Example Prompts

```
/shortcut-to-vibe
Import all my stories into VibeKanban project ai-agent-workforce at http://127.0.0.1:54271
```

```
/shortcut-to-vibe
Import https://app.shortcut.com/sandpip3rs/story/14 into VibeKanban at http://127.0.0.1:54271
```

```
/shortcut-to-vibe
Import https://app.shortcut.com/sandpip3rs/epic/5 and all its stories into VibeKanban at http://127.0.0.1:54271
```

## Notes

- `short search` returns up to 25 results by default — always pass `-l 100` for bulk imports
- The VibeKanban port changes on each restart — always confirm the current URL
- `sort_order` and `extension_metadata: null` are required by the remote issues API
