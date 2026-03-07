#!/usr/bin/env bash

#
# Licensed to Muhammad Hamadto 2026
# Licensed under the Apache License, Version 2.0
#
# Shortcut → VibeKanban Sync Helper
# Demonstrates the integration workflow between Shortcut, VibeKanban, and AI agents
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SHORTCUT_API_BASE="https://api.app.shortcut.com/api/v3"
VIBEKANBAN_URL="${VIBEKANBAN_URL:-http://localhost:3000}"

# Print colored message
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check Shortcut API token
    if [[ -z "${SHORTCUT_API_TOKEN:-}" ]]; then
        print_error "SHORTCUT_API_TOKEN not set"
        echo "  Get your token from: https://app.shortcut.com/settings/account/api-tokens"
        echo "  Then run: export SHORTCUT_API_TOKEN='your-token'"
        exit 1
    fi

    # Check curl
    if ! command -v curl &> /dev/null; then
        print_error "curl not found. Please install curl."
        exit 1
    fi

    # Check jq
    if ! command -v jq &> /dev/null; then
        print_warning "jq not found. Install for better JSON output: brew install jq"
    fi

    # Check VibeKanban
    if ! curl -s -f "${VIBEKANBAN_URL}" > /dev/null 2>&1; then
        print_warning "VibeKanban not accessible at ${VIBEKANBAN_URL}"
        echo "  Start VibeKanban: npx vibe-kanban"
    else
        print_success "VibeKanban is running at ${VIBEKANBAN_URL}"
    fi

    print_success "Prerequisites check complete"
}

# Test Shortcut connection
test_shortcut() {
    print_info "Testing Shortcut API connection..."

    response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/json" \
        -H "Shortcut-Token: ${SHORTCUT_API_TOKEN}" \
        "${SHORTCUT_API_BASE}/member")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [[ "$http_code" == "200" ]]; then
        if command -v jq &> /dev/null; then
            name=$(echo "$body" | jq -r '.profile.name // .profile.email_address')
            print_success "Connected as: $name"
        else
            print_success "Successfully connected to Shortcut"
        fi
    else
        print_error "Failed to connect to Shortcut (HTTP $http_code)"
        exit 1
    fi
}

# List Shortcut epics
list_epics() {
    print_info "Fetching Shortcut epics..."

    response=$(curl -s \
        -H "Content-Type: application/json" \
        -H "Shortcut-Token: ${SHORTCUT_API_TOKEN}" \
        "${SHORTCUT_API_BASE}/epics")

    if command -v jq &> /dev/null; then
        echo "$response" | jq -r '.[] | "\(.id): \(.name) (\(.state))"'
    else
        echo "$response"
    fi
}

# List stories from an epic
list_epic_stories() {
    local epic_id="$1"
    print_info "Fetching stories from epic $epic_id..."

    response=$(curl -s \
        -H "Content-Type: application/json" \
        -H "Shortcut-Token: ${SHORTCUT_API_TOKEN}" \
        "${SHORTCUT_API_BASE}/epics/${epic_id}/stories")

    if command -v jq &> /dev/null; then
        echo "$response" | jq -r '.[] | "\(.id): \(.name) [\(.workflow_state_id)]"'
    else
        echo "$response"
    fi
}

# Show usage examples
show_usage() {
    cat << EOF
${GREEN}Shortcut ↔ VibeKanban Integration Helper${NC}

${YELLOW}Usage:${NC}
  $0 check                    Check prerequisites
  $0 test                     Test Shortcut API connection
  $0 list-epics              List all Shortcut epics
  $0 list-stories EPIC_ID    List stories in an epic
  $0 workflow                Show example AI workflow commands

${YELLOW}Environment Variables:${NC}
  SHORTCUT_API_TOKEN         Your Shortcut API token (required)
  VIBEKANBAN_URL             VibeKanban URL (default: http://localhost:3000)

${YELLOW}Examples:${NC}
  # Check if everything is set up
  $0 check

  # List all epics
  $0 list-epics

  # List stories in epic 123
  $0 list-stories 123

  # Show AI workflow examples
  $0 workflow

${YELLOW}AI Integration:${NC}
  This script demonstrates the API calls. For full integration:

  1. Ensure Claude Code and Qwen Code have MCP servers configured
  2. Start VibeKanban: npx vibe-kanban
  3. Tell your AI: "Fetch Shortcut epic X and create VibeKanban tasks"

  The AI will use MCP to:
  - Query Shortcut API
  - Create tasks in VibeKanban
  - Start parallel agent work
  - Manage PRs automatically

${YELLOW}Documentation:${NC}
  See SHORTCUT_VIBEKANBAN_WORKFLOW.md for complete guide
EOF
}

# Show AI workflow examples
show_workflow() {
    cat << EOF
${GREEN}AI Workflow Command Examples${NC}

${YELLOW}1. Import Shortcut Epic to VibeKanban:${NC}
   "Fetch all stories from Shortcut epic 'User Authentication'
    and create tasks in VibeKanban project 'auth-service'"

${YELLOW}2. Start Parallel Work:${NC}
   "List all TODO tasks in VibeKanban project 'api-service'.
    Assign complex tasks to Claude team, simple tasks to Qwen agents.
    Start work in parallel."

${YELLOW}3. Task Status Check:${NC}
   "Show me the status of all tasks in VibeKanban project 'frontend-app'.
    Which tasks are in progress? Which are blocked?"

${YELLOW}4. Intelligent Routing:${NC}
   "Analyze all Shortcut stories in epic 'Q1 Goals'.
    Route security tasks to Claude, CRUD tasks to Qwen.
    Create VibeKanban tasks and start work."

${YELLOW}5. Daily Standup:${NC}
   "What did we complete yesterday in VibeKanban?
    What's in progress today?
    Any blockers?"

${YELLOW}6. Sprint Planning:${NC}
   "Import all Shortcut stories with label 'sprint-23' to VibeKanban.
    Estimate complexity and assign to appropriate agents."

${GREEN}How It Works:${NC}

  Your AI agents (Claude Code + Qwen Code) use MCP to:

  ┌─────────────┐
  │  Shortcut   │ ← Read stories via Shortcut MCP
  │   (via MCP) │
  └──────┬──────┘
         │
         ↓
  ┌─────────────┐
  │   AI Agent  │ ← Analyze and route work
  │ Claude/Qwen │
  └──────┬──────┘
         │
         ↓
  ┌─────────────┐
  │ VibeKanban  │ ← Create tasks via VibeKanban MCP
  │   (via MCP) │
  └──────┬──────┘
         │
         ↓
  ┌─────────────────────────┐
  │  Parallel Agent Teams   │ ← Work on tasks
  │  Claude + Qwen          │
  └─────────────────────────┘

${YELLOW}MCP Tools Available:${NC}

  Shortcut MCP:
  - list_stories, get_story, create_story
  - list_epics, search_stories
  - update_story, list_workflows

  VibeKanban MCP:
  - create_task, list_tasks, get_task
  - update_task, delete_task
  - start_workspace_session (launch agents)
  - list_projects, list_repos

${GREEN}Try it now!${NC}
  Tell Claude or Qwen: "Show me what Shortcut stories we have"
EOF
}

# Main script
main() {
    case "${1:-}" in
        check)
            check_prerequisites
            ;;
        test)
            check_prerequisites
            test_shortcut
            ;;
        list-epics)
            check_prerequisites
            list_epics
            ;;
        list-stories)
            if [[ -z "${2:-}" ]]; then
                print_error "Epic ID required"
                echo "Usage: $0 list-stories EPIC_ID"
                exit 1
            fi
            check_prerequisites
            list_epic_stories "$2"
            ;;
        workflow)
            show_workflow
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
