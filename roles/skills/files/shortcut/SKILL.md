---
name: shortcut
description: Interact with Shortcut project management. Fetch stories and epics, search, update state, and add comments using the short CLI.
---

# Shortcut Skill

Interact with Shortcut (project management) using the `short` CLI.

## Prerequisites

Verify the CLI is installed and authenticated before any operation:

```bash
which short || echo "short CLI not found — install via: npm install -g @shortcut-cli/shortcut-cli && short install"
short search -o me -l 1 2>/dev/null || echo "Not authenticated — run: short install"
```

## Core Commands

```bash
# Stories
short story <ID>                          # fetch story by ID
short search "<query>"                    # search stories
short search -o me                        # stories assigned to me
short search -s "In Progress"             # stories by state
short update <ID> -s "Done"              # update state
short update <ID> -t "New title"         # update title
short comment <ID> "comment text"        # add comment

# Epics
short epic <ID>                           # fetch epic by ID
short search --epic "<query>"             # search epics

# Workflows
short workflow                            # list workflow states
```

## Creating Stories

### Hierarchy

```
Objective  →  Epic  →  Story  →  Task
```

**Objective** — a major initiative or programme of work. Groups all its epics under one outcome.

**Epic = one feature, not a layer.** Never "all the database work" or "all the backend work." Always a deliverable piece of product value — something that can be demoed. All the work to ship it (database, API, frontend, ops, release) lives inside that one epic.

**Story = one deliverable inside a feature.** Written as a user story (`As a X, I want Y so that Z`). Description has two parts: plain-English "what and why" first, then technical notes after a `---` separator.

**Task = an individual contributor's personal to-do.** A checklist item someone writes for themselves inside a story. Granular, owned by one person, not a mini-story.

### Custom Fields

Set custom fields **per story, not per epic.** An epic spans multiple technical areas — the field must reflect what each individual story actually does, not what its parent epic is about.

| Field | Purpose | Rule |
|---|---|---|
| **Technical Area** | What kind of system work is this? (API, Database, Server, Client) | Set per story — a single epic will span multiple values |
| **Skill Set** | Who does this work? (Backend, Frontend, Techops, Product) | Reflects the discipline needed, not the team owning the epic |
| **Product Area** | Which product domain? (Integrations, Billing, etc.) | Usually consistent across all stories in an epic |

If the existing values do not cover the work, **create new custom field values** rather than forcing a poor fit.

This enables cross-cutting board views: filter `Technical Area = Database` to see all data work across every feature, or `Skill Set = Techops` to see all ops/release stories regardless of which epic they live in.

### Story Relationships

Use `relates to` to link child stories back to a parent story when a story has been broken into smaller pieces. Keeps traceability without forcing a rigid hierarchy.

### API Stories

Any story that defines or touches an API endpoint must be comprehensive. Use the [/api-design](../api-design/SKILL.md) skill to produce the full contract: URI, request headers/params/body, response codes and headers, all error codes, and endpoint completeness. A story without a complete API contract is not ready for development.

## URL Handling

Extract IDs from Shortcut URLs automatically:

- Story: `https://app.shortcut.com/<org>/story/<ID>` → use `short story <ID>`
- Epic: `https://app.shortcut.com/<org>/epic/<ID>` → use `short epic <ID>`

## API Reference

For detailed endpoint information, parameters, and response schemas, read:

```
reference/shortcut.openapi.json
```

Use this when constructing operations not covered by the CLI, or when you need to understand request/response shapes for a specific endpoint.

## Error Handling

- **CLI not found**: instruct user to `npm install -g @shortcut-cli/shortcut-cli`
- **Auth failure**: instruct user to run `short install` or set `SHORTCUT_API_TOKEN` env var
- **Story not found**: verify the ID, check workspace permissions
- **Rate limit**: wait and retry; Shortcut rate limits are per API token
