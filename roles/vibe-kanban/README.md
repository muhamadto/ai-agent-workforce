# VibeKanban Role

Installs and configures VibeKanban task management tool with Shortcut integration.

## What This Role Does

- Installs `vibe-kanban` globally via npm
- Deploys Shortcut-Vibe sync helper script to `~/.local/bin`
- Creates necessary directory structure

## Features

- **Local Kanban Board** - Visual task management in terminal
- **Shortcut Integration** - Bidirectional sync with Shortcut.com
- **CLI Workflow** - Developer-friendly command-line interface

## Usage

### Deploy VibeKanban

```bash
ansible-playbook playbook.yml -e setup_state=present --tags vibe-kanban
```

### Remove VibeKanban

```bash
ansible-playbook playbook.yml -e setup_state=absent --tags vibe-kanban
```

### Run VibeKanban

```bash
# Start local kanban board
vibe-kanban

# Sync tasks with Shortcut
shortcut-vibe-sync
```

## Files Deployed

- **Global npm package**: `vibe-kanban`
- **Sync script**: `~/.local/bin/shortcut-vibe-sync`

## Requirements

- Node.js and npm
- Shortcut.com account (for sync features)
- `~/.local/bin` in your `$PATH`

## Environment Variables

Configure Shortcut integration:

```bash
export SHORTCUT_API_TOKEN="your-api-token"
export SHORTCUT_WORKSPACE="your-workspace"
```

## Tags

- `tools` - Developer tools
- `kanban` - Kanban board tools
- `task-management` - Task management systems
