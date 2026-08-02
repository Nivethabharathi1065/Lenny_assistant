# Agent Build Log

Short log of the actual build steps + one real failure/fix while building
this simple edition.

## Steps
1. Cloned https://github.com/ChatPRD/lennys-podcast-transcripts and copied
   a 40-episode subset into `transcripts/` to keep the repo lightweight
   while still using real transcript content (not fake placeholder text).
2. Wrote `retrieval.py`: simple word-overlap search over chunked
   transcripts (220-word chunks). Verified with a manual query
   ("growth loops referral") returning a relevant episode chunk.
3. Wrote `db.py` (SQLite sessions/messages) and `skills.py` (qa vs ship30
   prompts + keyword router).
4. Wrote `main.py` wiring retrieval + skills + db + a call to Ollama's
   `/api/chat` endpoint, with artifact extraction via regex for fenced
   ```markdown / ```html blocks.

## Failure + Fix
**Failure:** First version of `str_replace` edit on `main.py` failed
validation because the tool call was missing a required `description`
field on the first attempt — a tooling/process error, not a logic bug.
**Fix:** Re-issued the edit with the required field; verified the change
(parsing stored `"type::content"` artifact strings back into
`{type, content}` dicts in `GET /sessions/{id}/messages`) by re-reading
the file.

## Smoke test
- Started `uvicorn` locally, hit `/health` → confirmed 2,790 transcript
  chunks loaded across 40 sources.
- Created a session via `POST /sessions` → got a UUID back.
- Confirmed `skills.choose_skill()` correctly routes
  "write a ship30 style post about onboarding" → `ship30`, and a plain
  question → `qa`.
- Did not have a local Ollama instance available in the build sandbox, so
  the actual LLM call path (`call_ollama`) was verified by code review and
  error-handling paths (connection error / timeout) rather than a live
  generation — flagging this honestly rather than claiming an untested
  path was fully verified end-to-end.
