# 🧠 AI Dev Agent – System Architecture

## Overview
This project implements an autonomous AI-powered software maintenance agent.  
It continuously runs tests, detects failures, identifies known or unknown bugs, applies patches, validates fixes, evaluates risk, and decides whether to merge, rollback, or escalate.

This is a full end-to-end closed-loop system, not a simple LLM script.

---

## Core Flow

1. Run test suite (`pytest`)
2. Detect failing tests
3. Match output to known bug signatures
4. Generate or apply patch
5. Re-run tests
6. Compute confidence score
7. Run safety & decision engine
8. Auto-merge, rollback, or escalate
9. Log and store memory

---

## Modules

### agent/auto_fix.py
Main orchestrator:
- Executes tests
- Applies patches
- Coordinates AI modules
- Enforces decision logic

### ai_reasoner.py
Generates a human-readable AI Fix Report:
- Root cause
- Patch explanation
- Test results
- Confidence

### confidence.py
Scores fixes based on:
- Bug type
- Patch size
- Test results
- Known vs learned bugs

Outputs a structured confidence object:
- confidence score
- decision (auto_merge / review)

### decision_engine.py
Acts as the AI safety gate.

Rules:
- Tests must pass
- Confidence must approve
- Diff size must be small
- Bug must not be flapping

Decisions:
- auto_merge
- rollback
- escalate

### ai_memory.py
Stores historical runs:
- Bugs
- Patches
- Decisions
- Confidence

Used to detect recurring failures.

### bug_db.json
Dynamic learned bug database.
The system expands its own knowledge over time.

---

## Safety Gates

This system cannot blindly write code.

Before any patch is accepted:
- Tests must pass
- Confidence engine must approve
- Diff must be small
- Bug must not reappear

Otherwise:
- Patch is rolled back automatically

---

## Why This Is Different

This is not a Copilot.
This is not a static analyzer.
This is not a chatbot.

This is an autonomous closed-loop AI maintenance agent:
- It changes real code
- Runs real tests
- Makes real decisions
- Maintains memory
- Protects itself from unsafe fixes

---

## Current Scope (Demo)

- Python codebase
- pytest test suite
- Known bug patterns
- Automatic learning of new bugs

This architecture scales to:
- Django / FastAPI
- CI pipelines
- GitHub PR generation
- Production monitoring

---

## Vision

This is the prototype of a true AI Software Engineer — not a helper, but a maintainer.
