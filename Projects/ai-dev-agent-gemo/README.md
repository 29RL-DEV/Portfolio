# AI Dev Agent (Learning Project)

## Overview
This project is a learning-focused implementation of a modular AI agent.
I built it to better understand how autonomous agents can be structured beyond simple LLM wrappers.

The goal was not to create a production-ready system, but to explore how reasoning, tool usage,
and basic safety boundaries can work together in a clean architecture.

## Why I Built This
Most AI examples I found online focus only on prompts.
I wanted to understand what actually happens around the model:
how decisions are made, how tools are selected, and how context is managed.

This project represents my learning process in building more structured AI systems.

## What It Does
- Takes user input
- Applies a reasoning step
- Optionally selects and executes tools
- Updates internal context (memory)
- Returns a controlled response

## Architecture (High Level)
- Agent core (orchestration)
- Reasoning logic
- Tool interface
- Memory handling

The structure is intentionally simple so each component can be understood and extended.

## AI Safety & Limitations
This project is not production-ready.
Some limitations are intentionally documented:
- Only basic protection against prompt injection
- Limited input validation
- No advanced policy enforcement

These are areas I would improve if continuing the project.

## What I Learned
- How to separate reasoning from execution
- Why tool access needs to be controlled
- How architectural decisions affect extensibility

## Notes
If extended further, the first improvements would be stronger validation
and clearer constraints around tool execution.
