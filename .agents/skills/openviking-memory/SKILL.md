---
name: openviking-memory
description: Persistent context and long-term memory for AI agents using OpenViking. Allows persisting project decisions, architecture notes, user preferences, and retrieving semantic context via viking:// URIs and the ov CLI.
metadata:
  short-description: OpenViking persistent agent memory
---

# OpenViking Persistent Memory for Antigravity

This skill equips the agent to store, retrieve, and manage long-term project context, architecture rules, and user preferences across sessions using **OpenViking** (`ov`).

## Core Concepts

OpenViking structures memory as a hierarchical **Virtual Filesystem** (`viking://`):
- `viking://~/`: Current user/session memory namespace.
- `viking://resources/`: Project resources, docs, codebase knowledge.
- `viking://skills/`: Installed capabilities and workflows.

## Retrieval & Search Workflow

Use `ov` CLI to inspect and query OpenViking:

1. **Semantic Search / Retrieval:**
   ```bash
   ov find "<semantic query>"
   ```
   Searches indexed memories and resources by concept or intent.

2. **Full Context-Aware Search:**
   ```bash
   ov search "<query>"
   ```

3. **Reading Resource or Memory Content:**
   ```bash
   # L2 - Full content
   ov read "viking://<path>"
   # L1 - Overview
   ov overview "viking://<path>"
   # L0 - Abstract / TL;DR
   ov abstract "viking://<path>"
   ```

4. **Navigating OpenViking Filesystem:**
   ```bash
   ov ls "viking://"
   ov tree "viking://"
   ```

## Writing & Committing Memory

1. **Add Durable Project / User Memory:**
   When the user asks to remember a project convention, architectural invariant, or preference:
   ```bash
   ov add-memory "Rule or decision text to remember"
   ```
   Or structured JSON:
   ```bash
   ov add-memory '{"role":"user","content":"Key invariant: Always maintain walk-forward backtest integrity"}'
   ```

2. **Add Resources to Index:**
   To index a file or documentation into OpenViking:
   ```bash
   ov add-resource ./docs/architecture/SYSTEM_ARCHITECTURE.md
   ```

## Server & Status Management

- Check health & connectivity:
  ```bash
  ov health
  ov status
  ```
- Configuration:
  ```bash
  ov config show
  ```
