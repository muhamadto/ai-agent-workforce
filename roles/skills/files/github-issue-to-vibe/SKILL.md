---
name: github-issue-to-vibe
description: Import GitHub issues into VibeKanban. Supports importing a single issue by URL or number, all open issues in a repo, issues assigned to me, or all issues in a milestone.
---

# GitHub Issue → VibeKanban Import Skill

Import GitHub issues into VibeKanban using the `gh` CLI and the VibeKanban REST API.

## Prerequisites

```bash
which gh || echo "gh CLI not found — install via: brew install gh"
gh auth status 2>/dev/null || echo "Not authenticated — run: gh auth login"
```

VibeKanban must be running. Ask the user for the URL (e.g. `http://127.0.0.1:54271`) — the port changes on each restart.

## Import Modes

### Mode 1: Single issue by URL or number

Extract owner, repo, and number from the URL if given (`https://github.com/<owner>/<repo>/issues/<number>`):

```bash
gh issue view <number> --repo <owner>/<repo> --json number,title,body,labels,milestone,assignees,state,url
```

### Mode 2: All open issues in a repo

```bash
gh issue list --repo <owner>/<repo> --state open --limit 100 \
  --json number,title,body,labels,milestone,assignees,state,url
```

### Mode 3: Issues assigned to me

```bash
gh issue list --repo <owner>/<repo> --assignee @me --state open --limit 100 \
  --json number,title,body,labels,milestone,assignees,state,url
```

### Mode 4: Issues in a milestone — imports milestone as parent + all child issues

```bash
# 1. List milestones to find the title and number
gh api repos/<owner>/<repo>/milestones

# 2. Fetch all issues in the milestone
gh issue list --repo <owner>/<repo> --milestone "<milestone title>" --state open --limit 100 \
  --json number,title,body,labels,milestone,assignees,state,url
```

Create the milestone as a parent issue in VibeKanban, then create each issue as a child using `parent_issue_id` (see Step 6 below).

## Step-by-Step Import

### 1. Discover the target VibeKanban project

If the user provides a VibeKanban URL, extract the `project_id` from the `/projects/<project_id>` segment. Ignore any `/issues/<issue_id>` suffix — that is just the page the user was on, not a parent to link to.

Otherwise, list local projects to find the org ID and available projects:

```bash
curl -s "http://127.0.0.1:<port>/api/projects"
```

Then list remote projects for the org:

```bash
curl -s "http://127.0.0.1:<port>/api/remote/projects?organization_id=<org_id>"
```

Ask the user which project to import into if not already specified. Note the `project_id` for subsequent steps.

### 2. Get the "To do" status ID

```bash
curl -s "http://127.0.0.1:<port>/api/remote/project-statuses?project_id=<project_id>"
```

Use the `id` of the status named `"To do"` as `status_id` in the create call.

### 3. Map GitHub labels to VibeKanban priority

Inspect the issue labels for priority signals:

| GitHub label (common patterns) | VibeKanban priority |
|---|---|
| priority: critical, P0, p0 | urgent |
| priority: high, P1, p1 | high |
| priority: medium, P2, p2 | medium |
| priority: low, P3, p3 | low |
| (no priority label) | null |

### 4. Check for duplicates (optional)

```bash
curl -s "http://127.0.0.1:<port>/api/remote/issues?project_id=<project_id>" | grep "gh-<owner>/<repo>#<number>"
```

Skip issues already present (matched by `[gh-<owner>/<repo>#<number>]` in description).

### 5. Create each issue

```bash
curl -s -X POST "http://127.0.0.1:<port>/api/remote/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<issue title>",
    "description": "[gh-<owner>/<repo>#<number>] https://github.com/<owner>/<repo>/issues/<number>\n\nLabels: <labels>\n\n<issue body>",
    "project_id": "<project_id>",
    "status_id": "<to_do_status_id>",
    "sort_order": <index>,
    "extension_metadata": null
  }'
```

- `sort_order`: use the issue's list position (0, 1, 2, …) to preserve ordering
- Always include `[gh-<owner>/<repo>#<number>]` and the GitHub URL for traceability
- Include labels in the description — VibeKanban has no equivalent field for GitHub labels

### 6. For milestone imports: link child issues

First create the milestone as a parent issue (Step 5), capture its returned `id`.
Then create each issue with `parent_issue_id` set:

```bash
curl -s -X POST "http://127.0.0.1:<port>/api/remote/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<issue title>",
    "description": "[gh-<owner>/<repo>#<number>] https://github.com/<owner>/<repo>/issues/<number>\n\nLabels: <labels>\n\n<issue body>",
    "project_id": "<project_id>",
    "status_id": "<to_do_status_id>",
    "sort_order": <index>,
    "parent_issue_id": "<milestone_issue_id>",
    "extension_metadata": null
  }'
```

## Example Prompts

```
/github-issue-to-vibe
Import https://github.com/sandpip3rs/ai-agent-workforce/issues/3 into VibeKanban at http://127.0.0.1:54271
```

```
/github-issue-to-vibe
Import all open issues from sandpip3rs/ai-agent-workforce into VibeKanban project ai-agent-workforce at http://127.0.0.1:54271
```

```
/github-issue-to-vibe
Import all issues assigned to me in sandpip3rs/ai-agent-workforce into VibeKanban at http://127.0.0.1:54271
```

```
/github-issue-to-vibe
Import milestone "v1.0" from sandpip3rs/ai-agent-workforce and all its issues into VibeKanban at http://127.0.0.1:54271
```

## Notes

- `gh issue list` returns up to 30 results by default — always pass `--limit 100` for bulk imports
- The VibeKanban port changes on each restart — always confirm the current URL
- `sort_order` and `extension_metadata: null` are required by the remote issues API
- If the user provides a VibeKanban URL, extract only the `project_id` from `/projects/<project_id>` — any `/issues/<id>` suffix is the current page, not a parent issue
