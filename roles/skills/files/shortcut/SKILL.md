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
