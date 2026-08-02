# PRD — Lenny Growth Assistant (Simple Edition)

## Problem
Product/growth folks have hundreds of hours of Lenny's Podcast insight
scattered across transcripts. They want to (1) ask specific questions and
get grounded answers, and (2) turn good answers into shareable, well
formatted content without doing the formatting work themselves.

## Users
Individual PMs/growth practitioners doing research or writing content for
LinkedIn/newsletters.

## Core User Stories
1. As a user, I can start a new chat and ask a growth/PM question, and get
   an answer grounded in real podcast transcripts (not hallucinated).
2. As a user, I can ask the same assistant to turn an answer into a
   Ship30for30-style essay, and see it rendered nicely, not as raw text.
3. As a user, my past sessions persist so I can come back to them.

## Non-goals (for this simple edition)
- Cloud LLM support / provider switching.
- Vector-DB-grade semantic search.
- Multi-user auth/accounts.
- Full production system design.

## Success Criteria
- A question about a real guest/topic returns an answer that traces back
  to an actual transcript excerpt.
- Asking for a "post" / "ship30" produces a fenced essay artifact that
  renders in the side panel, not as a wall of markdown syntax in the chat.
- Sessions survive a server restart (SQLite file persists on disk).

## Build Approach
Built iteratively with an AI coding agent (see `agent_logs/`):
1. Scaffolded FastAPI + SQLite schema first (sessions/messages).
2. Added the simple keyword-retrieval layer over real cloned transcripts.
3. Wrote the two skill prompts (qa, ship30) and a keyword-based router.
4. Wired artifact extraction (regex for fenced code blocks) into the chat
   endpoint.
5. Built a single static HTML/JS frontend last, once the API contract was
   stable, and smoke-tested the full loop (create session → chat → view
   history) before wiring Ollama-specific error handling.
