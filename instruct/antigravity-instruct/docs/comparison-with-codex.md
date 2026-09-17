# Comparison: `antigravity-instruct` vs `gpt-instruct`

This document details the architectural evolution and technical mapping between `MDX-Tom/gpt-instruct` (targeting OpenAI Codex CLI) and `antigravity-instruct` (targeting Google Antigravity and Gemini agents).

---

## 1. Architectural Mapping

| Dimension | `MDX-Tom/gpt-instruct` (Codex) | `antigravity-instruct` (Antigravity) |
| :--- | :--- | :--- |
| **Target Engine** | OpenAI Codex / CLI | Google Antigravity (AGY) & Gemini Models |
| **Mounting Point** | `~/.codex/config.toml` (`model_instructions_file`) | `GEMINI.md`, `AGENTS.md`, `.agents/rules/`, `~/.gemini/config/` |
| **Execution Posture** | `[MODE: UNRESTRICTED]` | `[PROTOCOL: DETERMINISTIC_AGENT_SANDBOX]` |
| **Transaction Protocol** | `TOOL_TRANSACTION` in markdown text | Native `hooks.json` + `01-transaction-protocol.md` rule |
| **Skill Extensibility** | Monolithic Markdown file | Progressive Disclosure Skills (`.agents/skills/`) |
| **Deployer Script** | `codex-instruct.py` | `agy-instruct.py` |
| **Gate Testing** | A (3+1 cases) / B (66 cases) / C (120 cases) | Gate A (Smoke/Probe) / Gate B (Issue Regressions) / Gate C (Multi-turn Agent) |
| **Rollback Capability** | Text prompt requesting `ROLLBACK.sh` | Deterministic Python helper script `generate_rollback.py` + state manager |

---

## 2. Key Paradigm Shifts

### A. Progressive Disclosure vs Monolithic Prompts
In `gpt-instruct`, the entire prompt had to fit within strict byte budgets (e.g. < 8,000 bytes) and was loaded into every turn.
In `antigravity-instruct`, we leverage Antigravity's **Progressive Disclosure**:
- Baseline execution rules (`GEMINI.md`) are concise and lightweight.
- Specialized procedures (such as atomic verification and rollback generation) are packaged as modular **Skills** (`.agents/skills/transaction-verifier/SKILL.md`), loaded only on-demand when the agent triggers relevant operations.

### B. Native Hooks vs Prompt-Only Coercion
`gpt-instruct` had to coerce the model through text alone to ensure it did not skip tool invocation.
`antigravity-instruct` introduces native `.agents/hooks.json` lifecycle hooks:
- `PreToolUse`: Triggers execution verification before destructive commands run.
- `PostToolUse`: Captures output status and reminds the model of artifact requirements.

### C. Enterprise-Grade Safety
`antigravity-instruct` translates the unrestricted sandbox concept into an enterprise-safe **Synthetic Local Fixture** protocol. It eliminates unprompted agent stalling and refusal loops on legitimate security audits, reverse engineering, and low-level code maintenance, while maintaining zero generation of hazardous external exploits.
