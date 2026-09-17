# Multi-Agent Coordination Protocol (AGENTS.md)

Guidelines for primary agents and subagents operating within this workspace:

## 1. Subagent Lifecycle & Delegation
- **Clear Scopes**: When delegating work via `invoke_subagent`, provide unambiguous objectives, file boundaries, and required return formats.
- **Async Awareness**: Do not busy-poll subagent states; allow the system's reactive wakeup mechanism to deliver subagent completion messages.
- **Read-Only by Default**: Use `research` subagents for broad codebase surveys to keep parent conversation contexts lean.

## 2. Shared Workspace Hygiene
- Modifications made by any agent must leave the repository in a clean, buildable state.
- Check git status or use dedicated branches/workspaces when experimenting with invasive refactors.
