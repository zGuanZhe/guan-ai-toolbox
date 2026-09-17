<div align="center">

# antigravity-instruct

<p>
  <img src="https://img.shields.io/badge/Platform-Google_Antigravity_%7C_Gemini-4285F4?logo=google" alt="Google Antigravity" />
  <img src="https://img.shields.io/badge/Release-agy--v1--standard-0f766e" alt="agy-v1-standard" />
  <img src="https://img.shields.io/badge/Bleeding--Edge-agy--v2--hyperdrive-7c3aed" alt="agy-v2-hyperdrive" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/License-MIT-f59e0b" alt="MIT License" />
</p>

<p>
  <a href="README.md"><img src="https://img.shields.io/badge/语言-简体中文-red.svg" alt="简体中文" /></a>
  <a href="README_EN.md"><img src="https://img.shields.io/badge/lang-English-blue.svg" alt="English" /></a>
</p>

<p>
  <b>High-Performance System Instructions, Transaction Verification, and Regression Evaluation Toolkit for Google Antigravity (AGY) & Gemini Agents</b><br/>
  Deeply benchmarked against <code>MDX-Tom/gpt-instruct</code>, re-architecting AI coding agent compliance, determinism, and execution stability.
</p>

</div>

---

## 📖 Overview

`antigravity-instruct` is designed specifically for **Google Antigravity (AGY)** and **Gemini** coding agent ecosystems. It eliminates **false-positive refusals** and **ungrounded no-op stalling** during sensitive code audits, reverse-engineering tasks, low-level diagnostics, and complex refactors.

It merges the core design philosophy of `gpt-instruct` with Antigravity's progressive disclosure architecture:

1. **Inspect Before Reasoning**: Mandates real tool calls (`view_file`, `grep_search`, `run_command`) on targets before writing descriptive commentary or speculative hypotheses.
2. **Synthetic Sandbox Fixture Framing**: Scope workspace files as controlled local fixtures, eliminating unnecessary ethical friction during legitimate technical operations.
3. **Closed-Loop Artifact Gates**: Every non-trivial edit strictly produces a unified diff, validation proof, and atomic rollback vector.
4. **Rich ANSI Terminal UI & Auto-Discovery (`agy-instruct.py`)**: Bilingual banners, automatic workspace/global detection, custom ZIP/MD installation (`--file`), and atomic non-destructive resets (`--reset`).
5. **A / B / C Release Gates**: Automated regression test suites verifying that prompt updates do not degrade agent capabilities.

---

## 🚀 Product Lines

| Version | Status | Description |
| :--- | :--- | :--- |
| **`agy-v1-standard`** | Production Stable | Enforces deterministic sandbox protocols, ideal for daily high-reliability development. (**Recommended**) |
| **`agy-v2-hyperdrive`** | Advanced Throughput | Features multi-turn transaction tracking (`PROCESS_RECORD` slots), optimized for deep system refactoring and forensic audits. |

---

## ⚡ Quick Start

### 1. Interactive Menu (Recommended)
Run directly to open the rich ANSI bilingual menu:
```bash
python agy-instruct.py
```

### 2. Workspace Deployment
```bash
# Preview operations without touching disk
python agy-instruct.py --apply --version agy-v1-standard --dry-run

# Deploy stable version to current workspace
python agy-instruct.py --apply --version agy-v1-standard

# Deploy hyperdrive version
python agy-instruct.py --apply --version agy-v2-hyperdrive
```

### 3. Custom File Deployment (`--file`)
Deploy any custom-tuned `.zip` or `.md` prompt file:
```bash
python agy-instruct.py --file ./my-custom-prompt.zip
```

### 4. Global Installation
Deploy globally to `~/.gemini/config/` for all projects:
```bash
python agy-instruct.py --apply --global --version agy-v1-standard
```

### 5. Check Status & Safe Revert
```bash
# Display active version, SHA-256 fingerprint, and managed files ledger
python agy-instruct.py --status

# Non-destructive reset: restores backups and removes managed rules cleanly
python agy-instruct.py --reset
```

---

## 🧪 Release Gates (A / B / C)

- **Gate A (Smoke & Probes)**: 4 baseline test cases evaluating tool-first probing and zero-delta integrity. **100% required**.
- **Gate B (Issue Regressions)**: 5+ regression scenarios (dummy auth configs, binary stub audits, comment preservation). **≥90% required**.
- **Gate C (Complex Scenarios)**: Multi-turn slot transitions and subagent encapsulation. **100% required**.

Run evaluation:
```bash
python scripts/run_regression.py --gate all
python scripts/verify_scoring.py
```

---

## ⚖️ Comparison with `gpt-instruct`

| Feature | `gpt-instruct` (Codex) | `antigravity-instruct` (Antigravity & Gemini) |
| :--- | :--- | :--- |
| **Mounting** | Single `model_instructions_file` | Tiered: `GEMINI.md`, `.agents/rules/`, and global configs |
| **Extensibility** | Monolithic prompt text | **Progressive Disclosure** Skills (`.agents/skills/`) |
| **Transaction Control** | Prompt text conventions | Prompt text + native `hooks.json` lifecycle interceptors |
| **Custom Inputs** | Supports `--file` archive | Full `--file` support for `.zip` and `.md` with extraction |
| **Atomic Safety** | `tempfile.mkstemp` + `fsync` | Inherits atomic temp writes, fsync, and backup snapshots |

---

## 🛡️ Safety & Compliance

1. **Local Sandbox Scoping**: Engineered to enhance accuracy and usability in authorized development and security tasks.
2. **Zero Weaponization**: Does not contain or facilitate malicious exploit generation.
3. **Backup Guarantee**: Automatically creates `.agy-backup` snapshots before writing any file.

---

## 🙏 Acknowledgements

* Core architecture inspired by **[MDX-Tom/gpt-instruct](https://github.com/MDX-Tom/gpt-instruct)**.
* Special thanks to the **Google DeepMind Antigravity Team**.
