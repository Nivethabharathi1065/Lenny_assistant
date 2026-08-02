# The Lenny Growth Assistant (Simple Edition)

A minimal, local-first version of the Lenny Growth Assistant: chat with an
AI grounded in real transcripts from *Lenny's Podcast*, and ask it to turn
answers into Ship30for30-style essays — rendered live in an artifact panel.

This is intentionally the **simple** version of the assignment: one
FastAPI file, one HTML file, SQLite instead of Postgres, Ollama only (no
cloud LLM toggle). It is fully functional end-to-end, just without the
extra infrastructure.

## Architecture Overview

```
frontend/index.html  --(fetch)-->  backend/main.py (FastAPI)
                                        |
                                        |-- retrieval.py  (keyword search over transcripts/*.md)
                                        |-- skills.py      (qa skill / ship30 skill prompt + router)
                                        |-- db.py          (SQLite: sessions + messages)
                                        |
                                        v
                                  Ollama (local LLM, http://localhost:11434)
```

**Flow for one chat turn:**
1. Frontend sends `{message, mode}` to `POST /sessions/{id}/chat`.
2. `skills.choose_skill()` decides **qa** vs **ship30**: explicit mode wins;
   otherwise it looks for trigger phrases like "write a post" / "ship30" /
   "newsletter" in the message.
3. `retrieval.search()` finds the top 5 transcript chunks (simple word-overlap
   scoring — no embeddings/vector DB, kept simple on purpose) matching the
   question.
4. The matching skill's system prompt + retrieved context + user message is
   sent to Ollama's `/api/chat`.
5. If the reply contains a ` ```markdown ` or ` ```html ` fenced block, it's
   extracted as an **artifact** and sent back separately so the frontend can
   render it live in the side panel (instead of just showing raw code).
6. Both messages are saved to SQLite so the session persists across reloads.

## Skills

- **Q&A skill** — answers strictly from the retrieved transcript excerpts,
  and says so honestly if nothing relevant was found instead of making
  things up.
- **Ship30for30 skill** — takes the same grounded context and rewrites it as
  a punchy, skimmable, ~1000–1250 word essay with a strong hook, bold text,
  bullets, and one clear takeaway, wrapped in a markdown code block so it
  renders as an artifact.

Routing is a simple keyword check (see `skills.py`) plus a manual
Auto / Q&A / Ship30 toggle in the UI, so you can always force a skill.

## Database Schema (SQLite — `backend/lenny.db`, auto-created)

```
sessions(id TEXT PK, title TEXT, created_at REAL)
messages(id TEXT PK, session_id TEXT FK, role TEXT, content TEXT,
         artifact TEXT NULL, created_at REAL)
```

`artifact` is stored as `"<type>::<content>"` (e.g. `"markdown::# Hook..."`)
and parsed back into `{type, content}` when messages are fetched.

> Swapping to Postgres (Supabase/Railway) later just means replacing
> `db.py`'s sqlite3 calls with SQLAlchemy + psycopg2 against the same schema.

## API Endpoints

| Method | Path                          | Description                        |
|--------|-------------------------------|-------------------------------------|
| GET    | `/health`                     | Ollama model + transcript stats     |
| POST   | `/sessions`                   | Create a new chat session           |
| GET    | `/sessions`                   | List all sessions                   |
| GET    | `/sessions/{id}/messages`     | Full message history for a session  |
| POST   | `/sessions/{id}/chat`         | Send a message, get a grounded reply|

## Setup & Run Locally

### 1. Install Ollama and pull a model
```bash
# https://ollama.com/download
ollama serve                # keep this running in one terminal
ollama pull llama3.2        # or any model that runs on your laptop
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
# optional overrides:
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2
uvicorn main:app --reload --port 8000
```

### 3. Frontend
Just open `frontend/index.html` in a browser (no build step — it's a
single static file that talks to `http://localhost:8000`).

### 4. Try it
- Ask: *"What does Brian Balfour say about growth loops?"* → Q&A skill.
- Ask: *"Turn that into a Ship30for30 post"* or toggle **Ship30** → essay
  artifact renders in the right panel.

## Environment Variables

| Variable       | Default                  | Purpose                     |
|----------------|---------------------------|------------------------------|
| `OLLAMA_URL`   | `http://localhost:11434`  | Ollama server address        |
| `OLLAMA_MODEL` | `llama3.2`                | Which local model to use     |

No API keys are needed for the simple/local version, and none are
committed to this repo.

## Transcript Data

40 real episodes from https://github.com/ChatPRD/lennys-podcast-transcripts
are included under `transcripts/` (a subset, kept small on purpose so the
repo stays lightweight — swap in the full set by copying more
`episodes/*/transcript.md` files in).

## Known Simplifications (vs. full spec)

- SQLite instead of Postgres/Supabase/Railway.
- Ollama only — no cloud LLM (Anthropic/OpenAI) toggle wired up.
- Keyword-overlap retrieval instead of embeddings/vector DB.
- Markdown artifact rendering in the frontend is a light regex-based
  renderer (bold + bullets), not a full Markdown parser.

These were cut deliberately to ship a working, honest demo instead of a
half-built complex one.
