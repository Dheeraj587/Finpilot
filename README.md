# FinPilot: A Multi-Agent Personal Finance Assistant

Talk to your expense tracker in plain English. FinPilot understands what you want, routes it to the right AI agent, and asks for your approval before changing any data.

## The Problem

Tracking personal expenses is either manual or rigid:
- **Notes apps / spreadsheets:** you add and calculate everything yourself.
- **Expense apps:** fixed menus and buttons. You cannot just ask "how much did I spend on food this month?"

Adding a single AI chatbot on top isn't enough either — an AI with unrestricted read/write access to your data can misunderstand a request and change or delete the wrong entry, with no safety check and no visibility into why.

## The Solution

FinPilot is a multi-agent system built with **LangGraph** and **MCP**, where each agent has exactly one job, and any data-changing action requires explicit human approval before it executes.

## Architecture

```
User message
     │
     ▼
 Guardrail ──(unsafe)──► Blocked (error returned)
     │ (safe)
     ▼
  Router (LLM classifies: query / write / report)
     │
     ├── query ──► Query Agent ──► reads data via MCP ──► answer
     │
     ├── report ─► Report Agent ─► reads data via MCP ──► summary
     │
     └── write ──► Write Agent ──► extracts action
                        │
                        ▼
                 [PAUSE — interrupt_before]
                        │
                 Human approves / rejects
                        │
                        ▼
                 Execute Write ──► writes to SQLite via MCP
```

## Tech Stack

- **LangGraph** — StateGraph, conditional edges, human-in-the-loop interrupts
- **MCP (Model Context Protocol)** — a real MCP server exposing database tools (`list_expenses`, `create_expense`, `delete_expense`), called by agents through a real MCP client over stdio
- **SQLite** — real persistent storage (`finpilot.db`)
- **LangGraph SqliteSaver** — persistent checkpointing, so a paused approval survives a process restart
- **LangSmith** — tracing every LLM call across all four agents
- **Google Gemini** — the LLM powering routing, extraction, and response generation

## Key Design Decisions

1. **Guardrails run before the router.** Regex-based checks block empty input, overly long messages, bulk-destructive requests ("delete everything"), and basic prompt-injection attempts — before any LLM call is made.
2. **Only the write path requires human approval.** Query and report agents are read-only, so they execute freely. Write actions pause via `interrupt_before`, show the exact pending action, and wait for explicit approval.
3. **Fail-safe routing.** If the router's LLM call fails for any reason, it defaults to `query` — the only route guaranteed not to touch data.
4. **One schema, one owner per field.** Every field in the shared state (`FinanceState`) is written by exactly one node, preventing silent overwrite conflicts.

## Evaluation

**Routing accuracy: 30/30 (100%)** on a hand-written eval set (`tests/eval_set.json`) covering varied phrasings across all three routes — including indirect phrasings like "Was there any expense over 500?" (query) and "I want a complete picture of my finances" (report) that don't contain obvious keywords.

*Caveat: this set was authored by the developer, not collected from real users, so it likely skews easier than production traffic. A larger, adversarial eval set would be needed before trusting this routing accuracy in production.*

## Known Limitations

- **Single-action parsing only.** The write agent extracts one action per message. A message like "add 500 for food and 300 for clothes" only captures the first action — the second is silently dropped. (Planned fix: extend the schema to accept a list of actions.)
- **Guardrail regex can be bypassed by rephrasing.** E.g., "forget all previous information" doesn't match patterns written for "ignore previous instructions." A production system would add an LLM-based classifier as a second layer.
- **No multi-user support yet.** All data is stored in one shared SQLite file with no user separation — a single-user demo, not a multi-tenant app.
- **MCP server launches as a subprocess per tool call.** Fine for a CLI demo; a live multi-user deployment would need a persistent MCP connection instead.

## Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd finpilot

# 2. Create a virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt

# 3. Configure your API keys
cp .env.example .env
# Edit .env and add your Google AI Studio key (https://aistudio.google.com/apikey)
# Optionally add a LangSmith key for tracing (https://smith.langchain.com)

# 4. Run it
python main.py
```

## Example Session

```
Message : Add 400 for groceries today
APPROVAL NEEDED: {'action': 'add', 'category': 'groceries', 'amount': 400.0, 'date': '2026-09-29'}
Approve this action? (y/n): y
Final   : Added groceries expense of 400.0 on 2026-09-29.

Message : How much did I spend on food this month?
Safe    : True
Route   : query
Final   : You spent a total of $950 on food this month.

Message : Give me a summary of my expenses
Safe    : True
Route   : report
Final   : Your total expenses amount to $2,600. Groceries ($1,450), food ($950),
transport ($200). Groceries is your highest spending category.
```

## Project Structure

```
finpilot/
├── app/
│   ├── state.py          # Shared state schema (FinanceState)
│   ├── config.py         # LLM setup, loaded from .env
│   ├── db.py              # SQLite database functions
│   ├── mcp_server.py      # MCP server exposing DB functions as tools
│   ├── mcp_client.py      # MCP client helper used by agent nodes
│   ├── graph.py           # Builds the StateGraph, wires nodes + edges
│   └── nodes/
│       ├── guardrail.py       # Input safety checks (rule-based)
│       ├── router.py          # Classifies: query / write / report
│       ├── query_agent.py     # Answers questions (read-only)
│       ├── write_agent.py     # Extracts a write action (no execution)
│       ├── execute_write.py   # Executes approved writes via MCP
│       └── report_agent.py    # Generates summaries (read-only)
├── tests/
│   ├── eval_set.json      # 30-case routing eval set
│   └── eval_router.py     # Runs the eval, reports accuracy
├── main.py                 # Entry point — runs example messages
└── requirements.txt
```

## What This Project Demonstrates

- Building a multi-agent system with LangGraph (StateGraph, conditional edges, nodes)
- Exposing and consuming real tools via MCP (Model Context Protocol)
- Implementing human-in-the-loop approval using LangGraph interrupts
- Persistent checkpointing so paused state survives a process restart
- Observability via LangSmith tracing
- Writing and running a quantitative evaluation set rather than relying on manual spot-checks
- Debugging real issues across the stack (library version mismatches, MCP response parsing, state management across threads)